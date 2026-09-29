import re
from typing import Tuple, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.conversation import ConversationMessage
from app.core.logging import logger

class IntentType:
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    ERP_ANALYTICS = "ERP_ANALYTICS"
    CONTEXTUAL = "CONTEXTUAL"

class ConversationRouter:
    @classmethod
    def classify_and_resolve(
        cls,
        question: str,
        language: str,
        conversation_id: Optional[str],
        db: Session,
        user: User,
    ) -> Tuple[str, str, List[Dict[str, str]]]:
        """
        Classifies incoming user question into GENERAL_CONVERSATION, ERP_ANALYTICS, or CONTEXTUAL.
        Resolves multi-turn contextual references using persisted conversation history.
        Returns: (detected_intent, resolved_question, recent_context)
        """
        q = question.strip().lower()
        recent_history: List[Dict[str, str]] = []

        # 1. Fetch recent history if conversation_id provided
        last_turn: Optional[ConversationMessage] = None
        if conversation_id:
            try:
                history_records = (
                    db.query(ConversationMessage)
                    .filter(
                        ConversationMessage.conversation_id == conversation_id,
                        ConversationMessage.user_id == user.id,
                    )
                    .order_by(ConversationMessage.timestamp.desc())
                    .limit(6)
                    .all()
                )
                # Reverse to chronological
                history_records.reverse()
                for rec in history_records:
                    recent_history.append({"role": "user", "content": rec.user_message})
                    recent_history.append({"role": "assistant", "content": rec.assistant_response})
                if history_records:
                    last_turn = history_records[-1]
            except Exception as e:
                logger.warning(f"Failed to retrieve conversation history: {e}")

        # 2. Check for Greetings / Pleasantries
        greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy",
            "مرحبا", "أهلا", "اهلا", "السلام عليكم", "صباح الخير", "مساء الخير"
        ]
        if any(q == g or q.startswith(g + " ") or q.startswith(g + "!") or q.startswith(g + ",") for g in greetings):
            # Check if it also asks for ERP data, e.g. "Hello, show me sales"
            if not any(k in q for k in ["sales", "revenue", "branch", "inventory", "stock", "product", "مبيعات", "فرع", "مخزون"]):
                logger.info(f"Intent classified as GENERAL_CONVERSATION (Greeting): '{question}'")
                return IntentType.GENERAL_CONVERSATION, question, recent_history

        # 3. Check for Capability questions
        capability_triggers = [
            "what can you do", "what can you help me with", "what can you help with", "help me",
            "what are your capabilities", "who are you", "what is your purpose", "how do you work",
            "ماذا يمكنك أن تفعل", "ماذا يمكنك ان تفعل", "ما هي قدراتك", "كيف يمكنك مساعدتي", "من أنت", "من انت"
        ]
        if any(tr in q for tr in capability_triggers):
            logger.info(f"Intent classified as GENERAL_CONVERSATION (Capability): '{question}'")
            return IntentType.GENERAL_CONVERSATION, question, recent_history

        # 4. Check for General Business / ERP Concept Definitions
        # e.g. "What is an invoice?", "What is a purchase order?", "Explain what ERP means", "Explain the difference between..."
        definition_starters = [
            "what is an ", "what is a ", "what does ", "explain what ", "define ", "meaning of ",
            "tell me about what is ", "what is the concept of ", "explain the difference", "difference between",
            "compare ", "compare between",
            "ما هو ", "ما هي ", "ما معنى ", "اشرح ما هو ", "اشرح ما هي ", "عرف ", "الفرق بين", "ما الفرق"
        ]
        business_concepts = [
            "invoice", "purchase order", "po", "erp", "ledger", "general ledger", "balance sheet",
            "chart of accounts", "depreciation", "accrual", "credit note", "debit note",
            "supply chain", "procurement", "inventory management", "bill of materials", "bom",
            "فاتورة", "أمر شراء", "امر شراء", "دفتر أستاذ", "ميزانية", "سلسلة إمداد", "إهلاك"
        ]
        is_concept_query = any(starter in q for starter in definition_starters) and any(concept in q for concept in business_concepts)
        exact_concept_matches = [
            "what is an invoice", "what is a purchase order", "explain what erp means", "what is erp",
            "ما هي الفاتورة", "ما هو أمر الشراء", "ما هو امر الشراء", "ما هو الـ erp", "ما هو erp"
        ]
        if is_concept_query or any(m in q for m in exact_concept_matches):
            logger.info(f"Intent classified as GENERAL_CONVERSATION (Concept Definition): '{question}'")
            return IntentType.GENERAL_CONVERSATION, question, recent_history

        # 5. Check for Politeness / Thanks / Farewells / General Chitchat
        courtesy = [
            "thank you", "thanks", "thanks a lot", "bye", "goodbye", "see you",
            "شكرا", "شكرا جزيلا", "مشكور", "مع السلامة", "وداعا"
        ]
        if any(q == c or q.startswith(c + " ") or q.endswith(" " + c) for c in courtesy):
            logger.info(f"Intent classified as GENERAL_CONVERSATION (Courtesy): '{question}'")
            return IntentType.GENERAL_CONVERSATION, question, recent_history

        general_chitchat = [
            "quote", "motivational quote", "motivational", "inspire", "inspiration",
            "tell me a joke", "joke", "who made you", "write a poem", "story",
            "حكمة", "اقتباس", "نكتة", "من صنعك", "أعطني حكمة", "اعطني حكمة"
        ]
        if any(tr in q for tr in general_chitchat):
            logger.info(f"Intent classified as GENERAL_CONVERSATION (Chitchat/Quote): '{question}'")
            return IntentType.GENERAL_CONVERSATION, question, recent_history

        # 6. Check for Contextual / Multi-turn Follow-ups
        contextual_triggers = [
            "which branch performed better", "which branch performed best", "which branch is highest",
            "which branch is better", "which branch won", "top branch among them",
            "what about last month", "what about last year", "what about the previous month",
            "how about last month", "and last month", "show me last month",
            "show me the same thing for", "same for", "what about",
            "why is that", "explain those numbers", "explain the results", "tell me why",
            "أي فرع كان أفضل", "اي فرع كان افضل", "أي فرع أفضل", "أي فرع أعلى",
            "ماذا عن الشهر الماضي", "ماذا عن الشهر السابق", "وماذا عن الشهر الماضي",
            "اشرح هذه الأرقام", "لماذا ذلك", "نفس الشيء لفرع"
        ]

        is_contextual_trigger = any(tr in q for tr in contextual_triggers) or (
            last_turn is not None and any(w in q for w in ["which one", "why", "how come", "what about", "ماذا عن", "أي واحد", "لماذا"])
        )

        if is_contextual_trigger:
            resolved_q = question
            if last_turn:
                prev_q = last_turn.user_message.lower()
                
                # Case A: "Which branch performed better?" or "Which branch is highest?"
                if any(w in q for w in ["which branch performed better", "which branch performed best", "which branch is highest", "which branch is better", "أي فرع كان أفضل", "اي فرع كان افضل"]):
                    if "sales" in prev_q or "مبيعات" in prev_q or "branch" in prev_q or "فرع" in prev_q:
                        resolved_q = "Which branch has the highest sales this month?" if language == "en" else "ما هو الفرع الأعلى مبيعات هذا الشهر؟"
                    else:
                        resolved_q = "Which branch has the highest sales?"

                    logger.info(f"Contextual follow-up resolved: '{question}' -> '{resolved_q}'")
                    return IntentType.CONTEXTUAL, resolved_q, recent_history

                # Case B: "What about last month?" / "ماذا عن الشهر الماضي؟"
                if any(w in q for w in ["last month", "الشهر الماضي", "الشهر السابق"]):
                    if "branch" in prev_q or "فرع" in prev_q:
                        resolved_q = "Show me sales by branch last month" if language == "en" else "المبيعات حسب الفرع الشهر الماضي"
                    elif "product" in prev_q or "منتج" in prev_q:
                        resolved_q = "Top products last month" if language == "en" else "أفضل المنتجات الشهر الماضي"
                    else:
                        resolved_q = "Total sales value last month" if language == "en" else "إجمالي المبيعات الشهر الماضي"

                    logger.info(f"Contextual follow-up resolved: '{question}' -> '{resolved_q}'")
                    return IntentType.CONTEXTUAL, resolved_q, recent_history

                # Case C: Explanation follow-up ("Why is that?", "Explain those numbers")
                if any(w in q for w in ["why is that", "explain those numbers", "explain the results", "لماذا ذلك", "اشرح هذه الأرقام"]):
                    logger.info(f"Contextual explanation request for: '{question}'")
                    return IntentType.CONTEXTUAL, question, recent_history

            # Even if no previous turn stored, if the user explicitly asks "Which branch performed better?",
            # we can route it to ERP analytics for highest branch!
            if any(w in q for w in ["which branch performed better", "which branch performed best", "أي فرع كان أفضل"]):
                return IntentType.CONTEXTUAL, "Which branch has the highest sales?", recent_history

        # 7. Check if question asks for ERP metrics or entities
        erp_keywords = [
            "sale", "sales", "revenue", "order", "orders", "inventory", "stock", "product", "products",
            "customer", "customers", "supplier", "suppliers", "branch", "branches", "category", "categories",
            "kpi", "trend", "profit", "units", "valuation", "performance", "top ", "highest", "lowest", "outstanding",
            "مبيعات", "إيرادات", "ايرادات", "فرع", "فروع", "مخزون", "منتج", "منتجات", "عملاء", "موردين", "أرباح", "ارباح", "فئات", "تصنيف", "طلب", "طلبات"
        ]
        if any(k in q for k in erp_keywords):
            logger.info(f"Intent classified as ERP_ANALYTICS: '{question}'")
            return IntentType.ERP_ANALYTICS, question, recent_history

        # Fallback to GENERAL_CONVERSATION for open dialogue
        logger.info(f"Intent classified as GENERAL_CONVERSATION (Open Dialogue): '{question}'")
        return IntentType.GENERAL_CONVERSATION, question, recent_history
