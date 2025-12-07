import SwiftUI

struct Particle: Hashable, Identifiable {
    let id = UUID()
    var x: Double
    var y: Double
    var speedX: Double
    var speedY: Double
    var scale: Double
    var opacity: Double
}

class ParticleSystem: ObservableObject {
    @Published var particles: [Particle] = []
    private var timer: Timer?
    
    init(count: Int = 20) {
        for _ in 0..<count {
            particles.append(createParticle())
        }
        startAnimation()
    }
    
    private func createParticle() -> Particle {
        return Particle(
            x: Double.random(in: 0...1),
            y: Double.random(in: 0...1),
            speedX: Double.random(in: -0.001...0.001),
            speedY: Double.random(in: -0.001...0.001),
            scale: Double.random(in: 0.5...1.5),
            opacity: Double.random(in: 0.2...0.6)
        )
    }
    
    private func startAnimation() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { [weak self] _ in
            self?.updateParticles()
        }
    }
    
    private func updateParticles() {
        for i in indices(particles) {
            particles[i].x += particles[i].speedX
            particles[i].y += particles[i].speedY
            
            // Bounce off edges
            if particles[i].x < 0 || particles[i].x > 1 { particles[i].speedX *= -1 }
            if particles[i].y < 0 || particles[i].y > 1 { particles[i].speedY *= -1 }
        }
    }
    
    private func indices(_ particles: [Particle]) -> Range<Int> {
        return 0..<particles.count
    }
}

struct ParticleBackgroundView: View {
    @StateObject private var system = ParticleSystem()
    @State var color: Color = .purple
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Color.black.ignoresSafeArea()
                
                // Gradient mesh
                RadialGradient(
                    gradient: Gradient(colors: [color.opacity(0.3), Color.black]),
                    center: .center,
                    startRadius: 50,
                    endRadius: geometry.size.width
                )
                .ignoresSafeArea()
                
                ForEach(system.particles) { particle in
                    Circle()
                        .fill(color)
                        .frame(width: 8 * particle.scale, height: 8 * particle.scale)
                        .position(
                            x: particle.x * geometry.size.width,
                            y: particle.y * geometry.size.height
                        )
                        .opacity(particle.opacity)
                        .blur(radius: 4)
                        .animation(.linear(duration: 0.05), value: particle.x)
                }
            }
        }
    }
}
