import SwiftUI

struct ChatView: View {
    @StateObject private var vm = ChatViewModel()
    @FocusState private var isFocused: Bool
    
    var body: some View {
        ZStack {
            // Novel Background
            ParticleBackgroundView(color: .purple)
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("Exa Scheduler")
                        .font(.system(size: 24, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                    Spacer()
                    Circle()
                        .fill(Color.green)
                        .frame(width: 8, height: 8)
                        .shadow(color: .green, radius: 4)
                }
                .padding()
                .background(.ultraThinMaterial)
                
                // Chat List
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(vm.messages) { msg in
                                MessageBubble(message: msg)
                            }
                            if vm.isLoading {
                                HStack {
                                    ProgressView()
                                        .tint(.white)
                                    Text("Thinking...")
                                        .foregroundStyle(.gray)
                                }
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.leading)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: vm.messages.count) { _ in
                        if let last = vm.messages.last {
                            withAnimation {
                                proxy.scrollTo(last.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                // Input Bar
                HStack(spacing: 12) {
                    TextField("Command the agent...", text: $vm.inputText)
                        .padding(12)
                        .background(Color.white.opacity(0.1))
                        .cornerRadius(20)
                        .focused($isFocused)
                        .foregroundStyle(.white)
                        .submitLabel(.send)
                        .onSubmit {
                            Task { await vm.sendMessage() }
                        }
                    
                    Button {
                        Task { await vm.sendMessage() }
                    } label: {
                        Image(systemName: "arrow.up.circle.fill")
                            .font(.system(size: 32))
                            .foregroundStyle(.white)
                            .symbolEffect(.bounce, value: vm.isLoading)
                    }
                    .disabled(vm.inputText.isEmpty || vm.isLoading)
                }
                .padding()
                .background(.ultraThinMaterial)
            }
        }
        .scrollDismissesKeyboard(.interactively)
    }
}

struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack {
            if message.isUser {
                Spacer()
                Text(message.text)
                    .padding()
                    .background(LinearGradient(colors: [.blue, .purple], startPoint: .leading, endPoint: .trailing))
                    .foregroundStyle(.white)
                    .cornerRadius(20, corners: [.topLeft, .topRight, .bottomLeft])
            } else {
                Text(message.text)
                    .padding()
                    .background(Color(white: 0.15))
                    .foregroundStyle(.white)
                    .cornerRadius(20, corners: [.topLeft, .topRight, .bottomRight])
                Spacer()
            }
        }
        .transition(.scale.combined(with: .opacity))
    }
}

// Extension to support specific corner rounding
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}
