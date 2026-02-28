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
        return "▶  Draw"
    }

    var body: some View {
        VStack(spacing: 8) {
            // Draw (full width)
            Button(action: onDraw) {
                Text(drawLabel)
                    .font(AppFonts.button)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 44)
            }
            .buttonStyle(SpiroButtonStyle(color: AppColors.btnDraw.opacity(engine.isDrawing ? 0.75 : 1.0)))

            // Undo + Clear row
            HStack(spacing: 8) {
                Button(action: onUndo) {
                    Text("↩  Undo")
                        .font(AppFonts.button)
                        .foregroundColor(engine.canUndo ? .white : .white.opacity(0.5))
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnUndo.opacity(engine.canUndo ? 1.0 : 0.4)))
                .disabled(!engine.canUndo)

                Button(action: onClear) {
                    Text("✕  Clear")
                        .font(AppFonts.button)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnClear))
            }

            // Random + Save row
            HStack(spacing: 8) {
                Button(action: onRandom) {
                    Text("🎲  Random")
                        .font(AppFonts.button)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnRandom))

                Button(action: onSave) {
                    Text("💾  Save")
                        .font(AppFonts.button)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 44)
                }
                .buttonStyle(SpiroButtonStyle(color: AppColors.btnSave))
            }
        }
        .padding(Layout.cardPadding)
        .background(AppColors.panel)
        .clipShape(RoundedRectangle(cornerRadius: Layout.cardRadius))
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
