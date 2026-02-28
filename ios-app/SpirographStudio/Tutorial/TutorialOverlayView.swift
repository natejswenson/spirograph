import SwiftUI

struct TutorialOverlayView: View {
    @Binding var isPresented: Bool
    @State private var currentStep = 0
    @State private var confettiParticles: [ConfettiParticle] = []

    private let totalSteps = 4

    var body: some View {
        ZStack {
            // Dimmed background
            Color.black.opacity(0.85)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                // Skip button
                HStack {
                    Spacer()
                    Button("Skip") {
                        dismiss()
                    }
                    .font(.system(size: 15, weight: .medium, design: .rounded))
                    .foregroundColor(.white.opacity(0.7))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(Color.white.opacity(0.12))
                    .clipShape(Capsule())
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)

                Spacer()

                // Step content
                stepContent(for: currentStep)
                    .transition(.asymmetric(
                        insertion: .opacity.combined(with: .offset(x: 40)),
                        removal: .opacity.combined(with: .offset(x: -40))
                    ))
                    .id(currentStep)

                Spacer()

                // Navigation
                VStack(spacing: 20) {
                    // Page dots
                    HStack(spacing: 8) {
                        ForEach(0..<totalSteps, id: \.self) { i in
                            Circle()
                                .fill(i == currentStep ? Color.white : Color.white.opacity(0.3))
                                .frame(width: 8, height: 8)
                                .animation(.easeInOut(duration: 0.2), value: currentStep)
                        }
                    }

                    // Navigation buttons
                    HStack(spacing: 16) {
                        if currentStep > 0 {
                            Button("← Back") {
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    currentStep -= 1
                                }
                            }
                            .font(.system(size: 15, weight: .medium, design: .rounded))
                            .foregroundColor(.white.opacity(0.7))
                            .padding(.horizontal, 24)
                            .padding(.vertical, 12)
                            .background(Color.white.opacity(0.12))
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                        }

                        Button(currentStep == totalSteps - 1 ? "Let's Go! 🚀" : "Next →") {
                            if currentStep == totalSteps - 1 {
                                dismiss()
                            } else {
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    currentStep += 1
                                }
                                haptic()
                            }
                        }
                        .font(.system(size: 17, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                        .padding(.horizontal, 32)
                        .padding(.vertical, 14)
                        .background(AppColors.btnDraw)
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                    }
                }
                .padding(.bottom, 48)
            }

            // Confetti on step 0
            if currentStep == 0 {
                ConfettiLayer(particles: confettiParticles)
                    .allowsHitTesting(false)
            }
        }
        .onAppear {
            confettiParticles = (0..<25).map { _ in ConfettiParticle() }
        }
    }

    // MARK: - Step Content

    @ViewBuilder
    private func stepContent(for step: Int) -> some View {
        switch step {
        case 0:
            TutorialStep(
                icon: "✦",
                iconColor: AppColors.btnDraw,
                title: "What is a Spirograph?",
                description: "A spirograph makes beautiful mathematical patterns — just like the toy! Watch as circles inside circles draw amazing curves.",
                highlight: nil
            )
        case 1:
            TutorialStep(
                icon: "🎚️",
                iconColor: AppColors.sliderSpeed,
                title: "Adjust the Wheels",
                description: "Drag the sliders to change the size of the circles and where the pen is. Try different combinations for unique patterns!",
                highlight: "Sliders"
            )
        case 2:
            TutorialStep(
                icon: "🎨",
                iconColor: AppColors.sliderr,
                title: "Pick a Color & Draw!",
                description: "Pick your favorite color, then tap Draw to watch the magic happen! Try Rainbow mode for a colorful spiral. ✨",
                highlight: "Draw"
            )
        case 3:
            TutorialStep(
                icon: "💾",
                iconColor: AppColors.btnSave,
                title: "Save & Share",
                description: "When you're done, save your artwork to Photos or share it with friends and family! 🎨",
                highlight: "Save"
            )
        default:
            EmptyView()
        }
    }

    // MARK: - Helpers

    private func dismiss() {
        withAnimation(.easeOut(duration: 0.4)) {
            isPresented = false
        }
    }

    private func haptic() {
        let gen = UIImpactFeedbackGenerator(style: .light)
        gen.prepare()
        gen.impactOccurred()
    }
}

// MARK: - Tutorial Step Card

struct TutorialStep: View {
    let icon: String
    let iconColor: Color
    let title: String
    let description: String
    let highlight: String?

    var body: some View {
        VStack(spacing: 24) {
            // Icon circle
            ZStack {
                Circle()
                    .fill(iconColor.opacity(0.2))
                    .frame(width: 100, height: 100)
                Text(icon)
                    .font(.system(size: 52))
            }

            // Title
            Text(title)
                .font(.system(size: 26, weight: .bold, design: .rounded))
                .foregroundColor(.white)
                .multilineTextAlignment(.center)

            // Description
            Text(description)
                .font(.system(size: 17, weight: .regular, design: .rounded))
                .foregroundColor(.white.opacity(0.85))
                .multilineTextAlignment(.center)
                .lineSpacing(4)
                .padding(.horizontal, 32)

            // Highlight chip
            if let highlight = highlight {
                Text("▶ \(highlight)")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundColor(iconColor)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
                    .background(iconColor.opacity(0.15))
                    .clipShape(Capsule())
                    .overlay(Capsule().stroke(iconColor.opacity(0.4), lineWidth: 1))
            }
        }
        .padding(.horizontal, 24)
    }
}

// MARK: - Confetti

struct ConfettiParticle: Identifiable {
    let id = UUID()
    let x: CGFloat = CGFloat.random(in: 0...1)
    let delay: Double = Double.random(in: 0...2)
    let duration: Double = Double.random(in: 3...5)
    let size: CGFloat = CGFloat.random(in: 6...14)
    let color: Color = AppColors.presets.randomElement() ?? .white
    let rotation: Double = Double.random(in: 0...360)
}

struct ConfettiLayer: View {
    let particles: [ConfettiParticle]

    var body: some View {
        GeometryReader { geo in
            ForEach(particles) { p in
                ConfettiDot(particle: p, height: geo.size.height)
                    .position(x: p.x * geo.size.width, y: 0)
            }
        }
        .ignoresSafeArea()
    }
}

struct ConfettiDot: View {
    let particle: ConfettiParticle
    let height: CGFloat
    @State private var yOffset: CGFloat = 0
    @State private var opacity: Double = 0

    var body: some View {
        Circle()
            .fill(particle.color)
            .frame(width: particle.size, height: particle.size)
            .offset(y: yOffset)
            .opacity(opacity)
            .rotationEffect(.degrees(particle.rotation + yOffset / 10))
            .onAppear {
                DispatchQueue.main.asyncAfter(deadline: .now() + particle.delay) {
                    withAnimation(.easeIn(duration: particle.duration).repeatForever(autoreverses: false)) {
                        yOffset = height + 50
                    }
                    withAnimation(.easeIn(duration: 0.3).delay(particle.delay)) {
                        opacity = 0.8
                    }
                }
            }
    }
}
