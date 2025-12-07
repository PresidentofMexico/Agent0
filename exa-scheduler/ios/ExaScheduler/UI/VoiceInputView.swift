import SwiftUI

struct VoiceInputView: View {
    @State private var phase = 0.0
    var isRecording: Bool
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<5) { index in
                RoundedRectangle(cornerRadius: 2)
                    .fill(Color.green)
                    .frame(width: 4, height: isRecording ? 20 + CGFloat.random(in: 0...10) : 4)
                    .animation(
                        isRecording 
                            ? .easeInOut(duration: 0.2).repeatForever().delay(Double(index) * 0.1) 
                            : .default,
                        value: isRecording
                    )
            }
        }
    }
}
