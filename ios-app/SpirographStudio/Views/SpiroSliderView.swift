import SwiftUI

struct SpiroSliderView: View {
    let emoji: String
    let label: String
    @Binding var value: Double
    let minValue: Double
    let maxValue: Double
    let accentColor: Color

    var body: some View {
        VStack(spacing: 4) {
            // Label row
            HStack {
                Text(emoji)
                    .font(.system(size: 14))
                Text(label)
                    .font(AppFonts.sliderLabel)
                    .foregroundColor(.white.opacity(0.85))
                Spacer()
                Text("\(Int(value))")
                    .font(AppFonts.sliderValue)
                    .foregroundColor(accentColor)
                    .frame(minWidth: 32, alignment: .trailing)
            }

            // Custom slider track
            CustomSliderTrack(value: $value,
                              minValue: minValue,
                              maxValue: maxValue,
                              accentColor: accentColor)
        }
        .frame(height: 48)
        .padding(.vertical, 2)
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
            let thumbSize: CGFloat = 22
            let frac = fraction(in: trackW)
            let thumbX = frac * (trackW - thumbSize) + thumbSize / 2

            ZStack(alignment: .leading) {
                // Background track
                Capsule()
                    .fill(AppColors.sliderTrack)
                    .frame(height: 6)

                // Filled portion
                Capsule()
                    .fill(accentColor)
                    .frame(width: max(thumbSize / 2, thumbX), height: 6)

                // Thumb
                Circle()
                    .fill(Color.white)
                    .frame(width: thumbSize, height: thumbSize)
                    .shadow(color: .black.opacity(0.3), radius: 2, x: 0, y: 1)
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
        .frame(height: 22)
    }
}
