import SwiftUI
import Foundation

struct Message: Identifiable, Hashable {
    let id = UUID()
    let text: String
    let isUser: Bool
    let timestamp = Date()
}

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var inputText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private let client = AgentClient()
    
    init() {
        // Initial greeting
        messages.append(Message(text: "Hello, I am Exa. How can I help you govern your schedule?", isUser: false))
    }
    
    func sendMessage() async {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        let userMsg = Message(text: inputText, isUser: true)
        messages.append(userMsg)
        let query = inputText
        inputText = ""
        isLoading = true
        errorMessage = nil
        
        do {
            let responseText = try await client.sendMessage(query)
            let agentMsg = Message(text: responseText, isUser: false)
            messages.append(agentMsg)
        } catch {
            errorMessage = "Failed to connect: \(error.localizedDescription)"
            messages.append(Message(text: "Error: \(error.localizedDescription)", isUser: false))
        }
        
        isLoading = false
    }
}
