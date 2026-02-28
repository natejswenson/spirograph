import SwiftUI

struct SpiroSliderView: View {
    let sfSymbol: String
    let label: String
    @Binding var value: Double
    let minValue: Double
    let maxValue: Double
    let accentColor: Color

    var body: some View {
        HStack(spacing: 8) {
            // Icon pill: colored circle with SF Symbol
            ZStack {
                Circle()
                    .fill(accentColor.opacity(0.22))
                    .frame(width: 26, height: 26)
                Image(systemName: sfSymbol)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(accentColor)
            }

            CustomSliderTrack(value: $value,
                              minValue: minValue,
                              maxValue: maxValue,
                              accentColor: accentColor)

            Text("\(Int(value))")
                .font(AppFonts.sliderValue)
                .foregroundColor(accentColor)
                .frame(width: 32, alignment: .trailing)
        }
        .frame(height: 22)
        .padding(.vertical, 7)   // extends touch target to 36pt without changing layout
        .contentShape(Rectangle())
    }
}

// MARK: - Custom Slider Track

struct CustomSliderTrack: View {
    @Binding var value: Double
    let minValue: Double
    let maxValue: Double
    let accentColor: Color

    @State private var isDragging = false

    private func fraction(in width: CGFloat) -> CGFloat {
        CGFloat((value - minValue) / (maxValue - minValue))
    }

    private func valueFromFraction(_ f: CGFloat) -> Double {
        let clamped = min(1, max(0, f))
        return Double(clamped) * (maxValue - minValue) + minValue
    }

    var body: some View {
        GeometryReader { geo in
            let trackW = geo.size.width
            let thumbSize: CGFloat = Layout.sliderThumbSize
            let frac = fraction(in: trackW)
            let thumbX = frac * (trackW - thumbSize) + thumbSize / 2

            ZStack(alignment: .leading) {
                // Background track
                Capsule()
                    .fill(AppColors.sliderTrack)
                    .frame(height: Layout.sliderHeight)

                // Filled portion — gradient
                Capsule()
                    .fill(LinearGradient(
                        colors: [accentColor.opacity(0.6), accentColor],
                        startPoint: .leading, endPoint: .trailing))
                    .frame(width: max(thumbSize / 2, thumbX), height: Layout.sliderHeight)

                // Thumb
                Circle()
                    .fill(Color.white)
                    .frame(width: thumbSize, height: thumbSize)
                    .shadow(color: accentColor.opacity(0.4), radius: 2, x: 0, y: 1)
                    .scaleEffect(isDragging ? 1.15 : 1.0)
                    .animation(.easeOut(duration: 0.1), value: isDragging)
                    .offset(x: thumbX - thumbSize / 2)
            }
            .frame(height: thumbSize)
            .contentShape(Rectangle())
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { gesture in
                        isDragging = true
                        let newFrac = gesture.location.x / trackW
                        let newVal = valueFromFraction(newFrac)
                        value = round(min(maxValue, max(minValue, newVal)))
                    }
                    .onEnded { _ in
                        isDragging = false
                    }
            )
        }
        .frame(height: Layout.sliderThumbSize)
    }
}
