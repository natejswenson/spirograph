import SwiftUI

struct ButtonsCard: View {
    @ObservedObject var engine: DrawingEngine
    let onDraw: () -> Void
    let onUndo: () -> Void
    let onClear: () -> Void
    let onRandom: () -> Void
    let onSave: () -> Void

    var drawGradient: LinearGradient {
        if engine.isDrawing {
            return LinearGradient(
                colors: [Color(red: 0.55, green: 0.2, blue: 0.85),
                         Color(red: 0.4,  green: 0.15, blue: 0.7)],
                startPoint: .leading, endPoint: .trailing)
        }
        return LinearGradient(
            colors: [Color(red: 0.35, green: 0.4,  blue: 0.95),
                     Color(red: 0.55, green: 0.25, blue: 0.9)],
            startPoint: .leading, endPoint: .trailing)
    }

    var body: some View {
        VStack(spacing: 6) {
            // Draw (full width, 42pt) — centered label + progress bar at bottom
            Button(action: onDraw) {
                HStack(spacing: 7) {
                    Image(systemName: engine.isDrawing ? "stop.fill" : "play.fill")
                        .font(.system(size: 13, weight: .semibold))
                    Text(engine.isDrawing
                         ? (engine.drawProgress > 0 ? "\(Int(engine.drawProgress * 100))%" : "Drawing…")
                         : "Draw")
                        .font(AppFonts.button)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 42)
                .background(drawGradient)
                .overlay(alignment: .bottom) {
                    if engine.isDrawing {
                        Capsule()
                            .fill(LinearGradient(
                                colors: [Color.white.opacity(0.25), Color.white.opacity(0.45)],
                                startPoint: .leading, endPoint: .trailing))
                            .frame(height: 3)
                            .scaleEffect(
                                x: CGFloat(max(0.02, engine.drawProgress)),
                                y: 1, anchor: .leading)
                            .animation(.linear(duration: 0.08), value: engine.drawProgress)
                            .padding(.horizontal, 10)
                            .padding(.bottom, 6)
                    }
                }
                .clipShape(RoundedRectangle(cornerRadius: Layout.buttonRadius))
            }
            .buttonStyle(GradientDrawButtonStyle())

            // 4 equal action buttons (36pt) — glass material
            HStack(spacing: 6) {
                Button(action: onUndo) {
                    GlassButtonLabel(symbol: "arrow.uturn.backward", text: "Undo")
                }
                .buttonStyle(GlassButtonStyle())
                .disabled(!engine.canUndo)
                .opacity(engine.canUndo ? 1.0 : 0.35)

                Button(action: onClear) {
                    GlassButtonLabel(symbol: "trash.fill", text: "Clear")
                }
                .buttonStyle(GlassButtonStyle())

                Button(action: onRandom) {
                    GlassButtonLabel(symbol: "shuffle", text: "Shuffle")
                }
                .buttonStyle(GlassButtonStyle())

                Button(action: onSave) {
                    GlassButtonLabel(symbol: "square.and.arrow.up", text: "Save")
                }
                .buttonStyle(GlassButtonStyle())
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
    }
}

// MARK: - Glass Button Label

private struct GlassButtonLabel: View {
    let symbol: String
    let text: String

    var body: some View {
        VStack(spacing: 2) {
            Image(systemName: symbol)
                .font(.system(size: 14, weight: .semibold))
            Text(text)
                .font(.system(size: 9, weight: .medium))
        }
        .frame(maxWidth: .infinity)
        .frame(height: 36)
    }
}

// MARK: - Button Styles

/// Gradient draw button — just handles press scale animation
struct GradientDrawButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}

/// Glass-material button style for the 4 action buttons
struct GlassButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundColor(.white)
            .background {
                ZStack {
                    RoundedRectangle(cornerRadius: Layout.buttonRadius)
                        .fill(.thinMaterial)
                    RoundedRectangle(cornerRadius: Layout.buttonRadius)
                        .fill(Color.white.opacity(0.08))
                }
            }
            .overlay {
                RoundedRectangle(cornerRadius: Layout.buttonRadius)
                    .stroke(AppColors.glassBorder, lineWidth: 1)
            }
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}

// Legacy style kept for compatibility
struct SpiroButtonStyle: ButtonStyle {
    let color: Color

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .background(color.opacity(configuration.isPressed ? 0.75 : 1.0))
            .clipShape(RoundedRectangle(cornerRadius: Layout.buttonRadius))
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}
