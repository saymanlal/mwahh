export interface User {
  id: string;
  user_uuid: string;
  email: string;
  anonymous_handle: string;
  email_verified: boolean;
  institutional_verified: boolean;
  gender: 'M' | 'F' | 'O';
  age?: number;
  height_cm?: number;
  bio?: string;
  profile_picture?: string;
  degree_or_profession?: string;
  interests: string[];
  city?: string;
  state?: string;
  country: string;
  scope: 'same_institute' | 'city' | 'state' | 'national' | 'global';
  preference_mode: 'friend' | 'hookup';
  age_preference_min: number;
  age_preference_max: number;
  height_preference_min?: number;
  height_preference_max?: number;
  tokens: number;
  active: boolean;
  last_active: string;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface Match {
  id: string;
  match_uuid: string;
  match_mode: 'friend' | 'hookup';
  match_score: number;
  status: 'active' | 'expired' | 'rejected';
  user1: User;
  user2: User;
  created_at: string;
  expires_at: string;
}

export interface ChatRoom {
  id: string;
  room_uuid: string;
  match: Match;
  status: 'active' | 'locked' | 'expired';
  message_count: number;
  created_at: string;
  expires_at: string;
  locked_at?: string;
  is_user_subscribed?: boolean;
  days_remaining?: number;
}

export interface ChatMessage {
  id: string;
  message_uuid: string;
  sender: User;
  message_type: 'text' | 'image' | 'voice' | 'gift' | 'sticker';
  content: string;
  media_url?: string;
  duration_seconds?: number;
  seen: boolean;
  seen_at?: string;
  created_at: string;
}

export interface Sticker {
  id: string;
  sticker_uuid: string;
  name: string;
  image_url: string;
  pack_name: string;
  premium: boolean;
  token_cost: number;
  created_at: string;
}

export interface Gift {
  id: string;
  gift_uuid: string;
  name: string;
  animation_url: string;
  premium: boolean;
  token_cost: number;
  created_at: string;
}

export interface Subscription {
  id: string;
  subscription_uuid: string;
  user: User;
  chat_room: ChatRoom;
  status: 'active' | 'expired' | 'cancelled';
  price_inr: number;
  started_at: string;
  expires_at: string;
  payment_id?: string;
}

export interface Notification {
  id: string;
  notification_uuid: string;
  notification_type:
    | 'new_message'
    | 'match'
    | 'payment_reminder'
    | 'chat_expiring'
    | 'chat_locked';
  title: string;
  body?: string;
  image_url?: string;
  voice_url?: string;
  read: boolean;
  dismissible: boolean;
  created_at: string;
  expires_at?: string;
}

export interface TokenTransaction {
  id: string;
  user: User;
  amount: number;
  transaction_type: 'gift' | 'sticker' | 'purchase';
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}
