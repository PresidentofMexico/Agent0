# Architecture Decision Record: Native iOS Agent Host

## Context
We need a high-performance, premium native frontend for the Exa Scheduler agent on iOS. The app must communicate with the Python Microservice (FastAPI) and provide a rich, responsive chat interface.

## Decisions

### 1. Stack Selection
- **Language**: Swift (5.9+)
- **UI Framework**: SwiftUI (declarative, reactive, modern)
- **Concurrency**: Swift Concurrency (async/await)

### 2. Architecture: MVVM-C (Model-View-ViewModel + Coordinator)
We will use MVVM to separate logic from UI, with a lightweight Coordinator pattern for navigation flow.

- **Models**: Plain Swift Structs matching the JSON/Pydantic schemas.
    - `ChatMessage` (id, role, content, timestamp)
    - `AgentQuery` (query text)
    - `AgentResponse` (response text)
- **Networking**: `AgentService` actor that handles `URLSession` requests to `http://localhost:8000`.
- **ViewModels**:
    - `ChatViewModel`: Manages the list of messages (`@Published var messages`), handles sending logic, and exposes states (`loading`, `idle`, `error`).
- **Views**:
    - `ChatView`: The main scrollable list of bubbles.
    - `InputBar`: Text field and voice input button.

### 3. UI/UX "Vibe"
- **Dark Mode First**: Sleek, OLED-black backgrounds with vibrant accent colors (Neon Purple/Blue).
- **Glassmorphism**: Visual depth using `ultraThinMaterial` on the input bar and headers.
- **Haptics**: Subtle feedback when sending messages or receiving responses.
- **Micro-interactions**: Animated bubbles appearing with a spring animation.

### 4. Code Snippets (Swift)

#### AgentService.swift
```swift
actor AgentService {
    let endpoint = URL(string: "http://localhost:8000/agent/chat")!
    
    func sendMessage(_ text: String) async throws -> String {
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["query": text]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(ChatResponse.self, from: data)
        return response.response
    }
}

struct ChatResponse: Codable {
    let response: String
}
```

#### ChatView.swift (Concept)
```swift
struct ChatView: View {
    @StateObject var vm = ChatViewModel()
    
    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(vm.messages) { msg in
                        MessageBubble(message: msg)
                    }
                }
            }
            .safeAreaInset(edge: .bottom) {
                InputBar(text: $vm.inputText, onSend: vm.send)
                    .background(.ultraThinMaterial)
            }
        }
        .background(Color.black.edgesIgnoringSafeArea(.all))
    }
}
```

## Future Considerations
- **Voice Mode**: Integrate Speech-to-Text (Apple Speech Framework) for hands-free queries.
- **Push Notifications**: For alerts from the server (requires Apple Developer Program).
