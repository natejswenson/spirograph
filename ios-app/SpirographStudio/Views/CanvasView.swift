import SwiftUI

struct CanvasView: View {
    @ObservedObject var engine: DrawingEngine
    @Binding var showToast: Bool
    @Binding var toastMessage: String

    // Floating preview params
    let R: Double
    let r: Double
    let d: Double
    let isRainbow: Bool
    let selectedColor: Color

    var body: some View {
        ZStack {
            // Canvas image — rounded corners
            Image(uiImage: engine.canvasImage)
                .resizable()
                .interpolation(.none)
                .aspectRatio(1, contentMode: .fit)
                .clipShape(RoundedRectangle(cornerRadius: Layout.canvasCornerRadius, style: .continuous))

            // Aura glow overlay — matches canvas corner radius
            RoundedRectangle(cornerRadius: Layout.canvasCornerRadius, style: .continuous)
                .stroke(
                    engine.isDrawing ? AppColors.canvasAuraDrawing : AppColors.canvasAuraIdle,
                    lineWidth: engine.isDrawing ? 6 : 3
                )
                .blur(radius: engine.isDrawing ? 14 : 8)
                .animation(.easeInOut(duration: 0.5), value: engine.isDrawing)

            // Floating mechanism preview — top-right corner
            VStack {
                HStack {
                    Spacer()
                    MechanismPreviewView(
                        R: R,
                        r: r,
                        d: d,
                        isDrawing: engine.isDrawing,
                        selectedColor: isRainbow ? .white : selectedColor
                    )
                    .frame(width: Layout.floatingPreviewSize, height: Layout.floatingPreviewSize)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(AppColors.glassBorder, lineWidth: 1)
                    }
                    .shadow(color: .black.opacity(0.35), radius: 8, y: 2)
                    .padding(8)
                }
                Spacer()
            }

            // Toast overlay
            if showToast {
                VStack {
                    ToastView(message: toastMessage)
                        .padding(.top, 12)
                    Spacer()
                }
                .transition(.asymmetric(
                    insertion: .opacity.combined(with: .offset(y: -10)),
                    removal: .opacity
                ))
            }
        }
        .animation(.easeInOut(duration: 0.3), value: showToast)
        .frame(maxWidth: .infinity)
        .aspectRatio(1, contentMode: .fit)
    }
}
