import SwiftUI

struct ToastView: View {
    let message: String

    var body: some View {
        Text(message)
            .font(AppFonts.toast)
            .foregroundColor(.white)
            .padding(.horizontal, 18)
            .padding(.vertical, 9)
            .background {
                ZStack {
                    Capsule().fill(.ultraThinMaterial)
                    Capsule().fill(Color.white.opacity(0.08))
                }
            }
            .overlay {
                Capsule()
                    .stroke(AppColors.glassBorder, lineWidth: 1)
            }
            .shadow(color: .black.opacity(0.4), radius: 12, y: 4)
    }
}

// MARK: - Toast Modifier

struct ToastModifier: ViewModifier {
    @Binding var isShowing: Bool
    let message: String

    func body(content: Content) -> some View {
        ZStack(alignment: .top) {
            content
            if isShowing {
                ToastView(message: message)
                    .padding(.top, 8)
                    .transition(.asymmetric(
                        insertion: .opacity.combined(with: .offset(y: -10)),
                        removal: .opacity
                    ))
                    .zIndex(100)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: isShowing)
    }
}

extension View {
    func toast(isShowing: Binding<Bool>, message: String) -> some View {
        modifier(ToastModifier(isShowing: isShowing, message: message))
    }
}
