import SwiftUI

struct ButtonsCard: View {
    @ObservedObject var engine: DrawingEngine
    let onDraw: () -> Void
    let onUndo: () -> Void
    let onClear: () -> Void
    let onRandom: () -> Void
    let onSave: () -> Void

    var drawLabel: String {
        if engine.isDrawing {
            let pct = Int(engine.drawProgress * 100)
            return "⏹  \(pct)%"
        }
        return "▶  D R A W"
    }

    var body: some View {
        VStack(spacing: 6) {
            // Draw (full width, 42pt)
            Button(action: onDraw) {
                Text(drawLabel)
                    .font(AppFonts.button)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 42)
            }
            .buttonStyle(SpiroButtonStyle(color: AppColors.btnDraw.opacity(engine.isDrawing ? 0.75 : 1.0)))

            // 4 equal action buttons (36pt)
            HStack(spacing: 6) {
                Button(action: onUndo) {
                    Text("↩ Undo")
                        .font(AppFonts.button)
                        .foregroundColor(engine.canUndo ? .white : .white.opacity(0.5))
                        .frame(maxWidth: .infinity)
                        .frame(height: 36)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnUndo.opacity(engine.canUndo ? 1.0 : 0.4)))
                .disabled(!engine.canUndo)

                Button(action: onClear) {
                    Text("✕ Clear")
                        .font(AppFonts.button)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 36)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnClear))

                Button(action: onRandom) {
                    Text("🎲")
                        .font(.system(size: 18))
                        .frame(maxWidth: .infinity)
                        .frame(height: 36)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnRandom))

                Button(action: onSave) {
                    Text("💾")
                        .font(.system(size: 18))
                        .frame(maxWidth: .infinity)
                        .frame(height: 36)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnSave))
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
    }
}

// MARK: - Button Style

struct SpiroButtonStyle: ButtonStyle {
    let color: Color

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .background(color.opacity(configuration.isPressed ? 0.75 : 1.0))
            .clipShape(RoundedRectangle(cornerRadius: Layout.buttonRadius))
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}
