'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

interface ChatMessage {
  id: string;
  sender_id: string;
  content: string;
  type: 'text' | 'image' | 'voice' | 'gift' | 'sticker';
  media_url?: string;
  created_at: string;
  seen: boolean;
}

interface UseChatsProps {
  roomId?: string;
  token?: string;
}

export function useChat({ roomId, token }: UseChatsProps) {
  const ws = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [typing, setTyping] = useState<string | null>(null);

  useEffect(() => {
    if (!roomId || !token) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/chat/${roomId}/?token=${token}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      console.log('[v0] WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'message') {
        setMessages((prev) => [...prev, data.message]);
      } else if (data.type === 'typing') {
        setTyping(data.user_handle);
        setTimeout(() => setTyping(null), 3000);
      } else if (data.type === 'seen') {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === data.message_id ? { ...msg, seen: true } : msg
          )
        );
      }
    };

    ws.current.onerror = (error) => {
      console.error('[v0] WebSocket error:', error);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [roomId, token]);

  const sendMessage = useCallback(
    (content: string, messageType: string = 'text', mediaUrl?: string) => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;

      ws.current.send(
        JSON.stringify({
          type: 'message',
          message_type: messageType,
          content,
          media_url: mediaUrl,
        })
      );
    },
    []
  );

  const sendTyping = useCallback(() => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    ws.current.send(JSON.stringify({ type: 'typing' }));
  }, []);

  const markAsSeen = useCallback((messageId: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    ws.current.send(JSON.stringify({ type: 'seen', message_id: messageId }));
  }, []);

  return {
    messages,
    isConnected,
    typing,
    sendMessage,
    sendTyping,
    markAsSeen,
  };
}
