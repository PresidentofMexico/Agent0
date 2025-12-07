import Foundation

enum AgentError: Error {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case serverError(String)
}

struct ChatRequest: Codable {
    let query: String
}

struct ChatResponse: Codable {
    let response: String
}

actor AgentClient {
    // In production, this should be configurable or loaded from Info.plist
    // For local dev: http://localhost:8000/agent/chat
    // For production: https://exa-scheduler-app.fly.dev/agent/chat
    private let endpoint = URL(string: "http://localhost:8000/agent/chat")!
    
    // Hardcoded for dev. In prod, use Keychain.
    private let apiSecret = "dev-secret-key"
    
    func sendMessage(_ text: String) async throws -> String {
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiSecret, forHTTPHeaderField: "X-Exa-Auth")
        request.timeoutInterval = 30 // Allow LLM time to think
        
        let body = ChatRequest(query: text)
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AgentError.serverError("Invalid response")
        }
        
        if !(200...299).contains(httpResponse.statusCode) {
             throw AgentError.serverError("Server returned code: \(httpResponse.statusCode)")
        }
        
        do {
            let result = try JSONDecoder().decode(ChatResponse.self, from: data)
            return result.response
        } catch {
            throw AgentError.decodingError(error)
        }
    }
}
