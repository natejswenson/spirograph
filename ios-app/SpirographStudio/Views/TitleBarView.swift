import SwiftUI

struct TitleBarView: View {
    let isDrawing: Bool
    let layerCount: Int

    @State private var pulseScale: CGFloat = 1.0

    var body: some View {
        HStack(spacing: 10) {
            Circle()
                .fill(isDrawing ? AppColors.dotDrawing : AppColors.dotIdle)
                .frame(width: 10, height: 10)
                .scaleEffect(pulseScale)
                .onChange(of: isDrawing) { _, drawing in
                    if drawing {
                        withAnimation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true)) {
                            pulseScale = 0.7
                        }
                    } else {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            pulseScale = 1.0
                        }
                    }
                }

            Text("Spirograph Studio")
                .font(AppFonts.title)
                .foregroundStyle(LinearGradient(
                    colors: [Color(red: 0.72, green: 0.78, blue: 1.0),
                             Color(red: 0.85, green: 0.60, blue: 1.0)],
                    startPoint: .leading, endPoint: .trailing))

            Spacer()

            // Layer count badge
            if isDrawing {
                HStack(spacing: 4) {
                    Image(systemName: "rays")
                        .font(.system(size: 10, weight: .semibold))
                    Text("Drawing…")
                        .font(AppFonts.status)
                }
                .foregroundColor(AppColors.dotDrawing)
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(AppColors.dotDrawing.opacity(0.15))
                .clipShape(Capsule())
                .transition(.opacity.combined(with: .scale(scale: 0.85)))
            } else if layerCount > 0 {
                HStack(spacing: 4) {
                    Image(systemName: "square.stack.fill")
                        .font(.system(size: 10, weight: .semibold))
                    Text("\(layerCount)")
                        .font(AppFonts.status)
                }
                .foregroundColor(AppColors.dotDrawing)
                .padding(.horizontal, 8)
                .padding(.vertical, 3)
                .background(AppColors.dotDrawing.opacity(0.15))
                .clipShape(Capsule())
                .transition(.opacity.combined(with: .scale(scale: 0.85)))
            }
        }
        .animation(.easeInOut(duration: 0.3), value: isDrawing)
        .animation(.easeInOut(duration: 0.3), value: layerCount)
        .padding(.horizontal, 16)
        .frame(height: 44)
        .background(.ultraThinMaterial)
        .overlay(alignment: .bottom) {
            Rectangle()
                .fill(AppColors.glassBorder)
                .frame(height: 1)
        }
    }
}
