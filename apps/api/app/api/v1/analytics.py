from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsQueryRequest,
    AnalyticsQueryResponse,
    ConversationHistoryResponse,
    ConversationMessageSchema,
    ConversationListResponse,
    ConversationSummaryItem,
    UserPreferenceSchema,
    UserPreferenceResponse,
)
from app.ai.workflow import analytics_workflow
from app.security.rbac import get_current_user
from app.models.user import User
from app.models.conversation import ConversationMessage
from app.models.user_preference import UserPreference

router = APIRouter(prefix="/analytics", tags=["AI Analytics & Conversation"])

@router.post("/query", response_model=AnalyticsQueryResponse)
def execute_analytics_query(
    request: AnalyticsQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unified entry point for AI conversations and ERP analytics.
    Intelligently routes to GENERAL_CONVERSATION, ERP_ANALYTICS, or CONTEXTUAL resolution.
    Strictly preserves RBAC, branch restrictions, and SQL security guardrails.
    """
    return analytics_workflow.execute_workflow(db, current_user, request)

@router.get("/conversations", response_model=ConversationListResponse)
def list_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists distinct conversation threads belonging to the authenticated user."""
    # Find unique conversation_ids for this user
    rows = (
        db.query(
            ConversationMessage.conversation_id,
            func.max(ConversationMessage.timestamp).label("last_activity"),
            func.count(ConversationMessage.id).label("msg_count"),
        )
        .filter(ConversationMessage.user_id == current_user.id)
        .group_by(ConversationMessage.conversation_id)
        .order_by(func.max(ConversationMessage.timestamp).desc())
        .limit(20)
        .all()
    )

    summaries = []
    for r in rows:
        conv_id = r[0]
        last_rec = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == conv_id)
            .order_by(ConversationMessage.timestamp.desc())
            .first()
        )
        if last_rec:
            summaries.append(
                ConversationSummaryItem(
                    conversation_id=conv_id,
                    last_message=last_rec.user_message[:80],
                    last_response=last_rec.assistant_response[:120],
                    last_intent=last_rec.detected_intent,
                    updated_at=last_rec.timestamp,
                    message_count=r[2],
                )
            )

    return ConversationListResponse(conversations=summaries)

@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetches chronological messages for a specific conversation belonging to the user."""
    records = (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.conversation_id == conversation_id,
            ConversationMessage.user_id == current_user.id,
        )
        .order_by(ConversationMessage.timestamp.asc())
        .all()
    )

    messages = [
        ConversationMessageSchema(
            id=rec.id,
            conversation_id=rec.conversation_id,
            user_id=rec.user_id,
            role=rec.role,
            user_message=rec.user_message,
            assistant_response=rec.assistant_response,
            detected_intent=rec.detected_intent,
            timestamp=rec.timestamp,
            audit_reference=rec.audit_reference,
        )
        for rec in records
    ]

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        total_messages=len(messages),
        messages=messages,
    )

@router.get("/preferences", response_model=UserPreferenceResponse)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves the authenticated user's UI & conversational preferences."""
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        return UserPreferenceResponse(
            user_id=current_user.id,
            preferred_language="en",
            preferred_response_style="concise",
            preferred_report_format="table_and_chart",
            terminology_preference="standard",
        )
    return UserPreferenceResponse(
        user_id=current_user.id,
        preferred_language=pref.preferred_language,
        preferred_response_style=pref.preferred_response_style,
        preferred_report_format=pref.preferred_report_format,
        terminology_preference=pref.terminology_preference,
    )

@router.put("/preferences", response_model=UserPreferenceResponse)
def update_user_preferences(
    prefs: UserPreferenceSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the authenticated user's UI & conversational preferences.
    CRITICAL: Preferences alter only response styling and UI options; permissions remain backend-authoritative.
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            preferred_language=prefs.preferred_language,
            preferred_response_style=prefs.preferred_response_style,
            preferred_report_format=prefs.preferred_report_format,
            terminology_preference=prefs.terminology_preference,
        )
        db.add(pref)
    else:
        pref.preferred_language = prefs.preferred_language
        pref.preferred_response_style = prefs.preferred_response_style
        pref.preferred_report_format = prefs.preferred_report_format
        pref.terminology_preference = prefs.terminology_preference
        pref.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(pref)

    return UserPreferenceResponse(
        user_id=current_user.id,
        preferred_language=pref.preferred_language,
        preferred_response_style=pref.preferred_response_style,
        preferred_report_format=pref.preferred_report_format,
        terminology_preference=pref.terminology_preference,
    )

@router.get("/db-migration-status")
def get_migration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to verify database migration status.
    Determines whether conversation_messages and user_preferences tables exist in production Neon database.
    """
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required to view database migration status.")
    from app.core.migration import get_db_migration_status, run_safe_migration
    stat = get_db_migration_status()
    if not stat["migration_applied"]:
        run_res = run_safe_migration()
        stat = run_res["status"]
    return stat

@router.get("/ai-provider-status")
def get_ai_provider_status(
    current_user: User = Depends(get_current_user),
):
    """
    Admin-only endpoint to verify live OpenAI configuration and real API connectivity.
    Never exposes API keys or secrets.
    """
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    
    from app.ai.openai_provider import OpenAIProvider
    import httpx
    provider = OpenAIProvider()
    has_key = provider.has_api_key()
    
    test_result = "not_tested"
    test_error = None
    if has_key:
        try:
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": settings.OPENAI_MODEL, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1}
            with httpx.Client(timeout=10.0) as client:
                res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    test_result = "success"
                else:
                    test_result = "failure"
                    if res.status_code == 401:
                        test_error = "invalid_key"
                    elif res.status_code == 429:
                        test_error = "insufficient_quota_or_billing"
                    else:
                        test_error = f"http_{res.status_code}"
        except httpx.ConnectError:
            test_result = "failure"
            test_error = "network_failure"
        except Exception as e:
            test_result = "failure"
            test_error = type(e).__name__
    else:
        test_result = "skipped"
        test_error = "missing_key"
        
    return {
        "ai_provider": settings.AI_PROVIDER,
        "openai_model": settings.OPENAI_MODEL,
        "openai_key_configured": has_key,
        "real_api_call_status": test_result,
        "error_category": test_error,
    }


