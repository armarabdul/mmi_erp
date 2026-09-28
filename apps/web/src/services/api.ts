const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('mmi_auth_token');
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  try {
    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
      localStorage.removeItem('mmi_auth_token');
      localStorage.removeItem('mmi_user');
      if (!window.location.pathname.includes('/login')) {
        window.dispatchEvent(new CustomEvent('mmi_auth_unauthorized'));
      }
      throw new ApiError(401, 'Session expired. Please log in again.');
    }

    if (!res.ok) {
      let errorData;
      try {
        errorData = await res.json();
      } catch {
        errorData = { message: res.statusText };
      }
      const message = errorData.detail || errorData.message || `Request failed with status ${res.status}`;
      throw new ApiError(res.status, message, errorData);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(0, err.message || 'Network connection failed. Please check backend server.');
  }
}

export async function downloadReportFile(
  reportId: string,
  format: 'xlsx' | 'pdf' | 'docx' | 'csv',
  lang: 'en' | 'ar' = 'en'
): Promise<void> {
  const token = localStorage.getItem('mmi_auth_token');
  const url = `${API_BASE_URL}/reports/${reportId}/export?format=${format}&lang=${lang}&limit=1000`;
  
  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!res.ok) {
    throw new Error('Failed to download report export.');
  }

  const blob = await res.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `MMI_${reportId}_${lang}.${format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}
