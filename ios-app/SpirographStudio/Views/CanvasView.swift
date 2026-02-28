import SwiftUI

struct CanvasView: View {
    @ObservedObject var engine: DrawingEngine
    @Binding var showToast: Bool
    @Binding var toastMessage: String

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
