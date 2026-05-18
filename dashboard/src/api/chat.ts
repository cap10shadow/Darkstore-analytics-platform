import { chatPost } from './client'

export interface ChatResponse {
  response: string
  [key: string]: unknown
}

export const sendMessage = (message: string) =>
  chatPost<ChatResponse>('/chat', { message })
