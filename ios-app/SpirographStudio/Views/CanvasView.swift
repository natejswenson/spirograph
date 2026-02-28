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
            // Canvas image
            Image(uiImage: engine.canvasImage)
                .resizable()
                .interpolation(.none)
                .aspectRatio(1, contentMode: .fit)

            // Aura glow overlay (border glow)
            Rectangle()
                .fill(Color.clear)
                .overlay {
                    RoundedRectangle(cornerRadius: 0)
                        .stroke(
                            engine.isDrawing ? AppColors.canvasAuraDrawing : AppColors.canvasAuraIdle,
                            lineWidth: 4
                        )
                        .blur(radius: 12)
                }
                .animation(.easeInOut(duration: 0.4), value: engine.isDrawing)

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
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
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
