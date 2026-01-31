export class AppError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number = 400,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const API_ERRORS = {
  INVALID_EMAIL: new AppError('INVALID_EMAIL', 'Invalid email format', 400),
  EMAIL_NOT_VERIFIED: new AppError(
    'EMAIL_NOT_VERIFIED',
    'Email not verified. Please check your inbox.',
    403
  ),
  NOT_INSTITUTIONAL: new AppError(
    'NOT_INSTITUTIONAL',
    'Email domain not recognized as institutional',
    403
  ),
  INVALID_OTP: new AppError('INVALID_OTP', 'Invalid or expired OTP', 400),
  USER_NOT_FOUND: new AppError('USER_NOT_FOUND', 'User not found', 404),
  UNAUTHORIZED: new AppError('UNAUTHORIZED', 'Unauthorized', 401),
  INSUFFICIENT_TOKENS: new AppError(
    'INSUFFICIENT_TOKENS',
    'Insufficient tokens',
    402
  ),
  CHAT_LOCKED: new AppError('CHAT_LOCKED', 'Chat is locked', 403),
  CHAT_EXPIRED: new AppError('CHAT_EXPIRED', 'Chat has expired', 410),
  PAYMENT_REQUIRED: new AppError(
    'PAYMENT_REQUIRED',
    'Payment required to continue',
    402
  ),
  RATE_LIMITED: new AppError('RATE_LIMITED', 'Too many requests', 429),
  SERVER_ERROR: new AppError(
    'SERVER_ERROR',
    'An unexpected error occurred',
    500
  ),
};

export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}

export function formatError(error: unknown): {
  message: string;
  code?: string;
} {
  if (isAppError(error)) {
    return {
      message: error.message,
      code: error.code,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  return {
    message: 'An unexpected error occurred',
  };
}
