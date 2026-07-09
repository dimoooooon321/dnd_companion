import axios from 'axios';

type ApiErrorResponse = {
  detail?: string | Array<{ msg?: string; message?: string }>;
  message?: string;
};

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong.') {
  if (axios.isAxiosError(error)) {
    const responseData = error.response?.data as ApiErrorResponse | string | undefined;

    if (typeof responseData === 'string') {
      return responseData;
    }

    if (responseData?.detail) {
      if (typeof responseData.detail === 'string') {
        return responseData.detail;
      }

      return responseData.detail
        .map((item) => item.message ?? item.msg)
        .filter(Boolean)
        .join(', ');
    }

    if (responseData?.message) {
      return responseData.message;
    }

    return error.message || fallback;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}
