'use client';

interface ChatMessageProps {
  message: {
    id: string;
    sender_id: string;
    content: string;
    type: 'text' | 'image' | 'voice' | 'gift' | 'sticker';
    media_url?: string;
    created_at: string;
    seen: boolean;
  };
  isOwn: boolean;
  senderHandle: string;
}

export function ChatMessage({ message, isOwn, senderHandle }: ChatMessageProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const bgColor = isOwn
    ? 'bg-blue-500 text-white'
    : 'bg-gray-200 text-gray-900';
  const alignment = isOwn ? 'justify-end' : 'justify-start';

  return (
    <div className={`flex ${alignment} mb-3`}>
      <div className="max-w-xs">
        {!isOwn && (
          <p className="text-xs text-gray-600 mb-1">{senderHandle}</p>
        )}
        {message.type === 'text' && (
          <div className={`${bgColor} rounded-lg px-3 py-2`}>
            <p className="break-words">{message.content}</p>
          </div>
        )}
        {message.type === 'image' && (
          <img
            src={message.media_url || "/placeholder.svg"}
            alt="message image"
            className="rounded-lg max-w-full"
          />
        )}
        {message.type === 'voice' && (
          <audio
            controls
            className="w-full"
            src={message.media_url}
            crossOrigin="anonymous"
          />
        )}
        {message.type === 'sticker' && (
          <img
            src={message.media_url || "/placeholder.svg"}
            alt="sticker"
            className="w-20 h-20"
          />
        )}
        {message.type === 'gift' && (
          <div className={`${bgColor} rounded-lg px-3 py-2`}>
            <p className="text-sm">🎁 Gift: {message.content}</p>
          </div>
        )}
        <p className="text-xs mt-1 opacity-75">
          {formatTime(message.created_at)}
          {isOwn && message.seen && ' ✓✓'}
        </p>
      </div>
    </div>
  );
}
