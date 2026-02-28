import SwiftUI

struct ColorPickerCard: View {
    @Binding var selectedColorIndex: Int
    @Binding var isRainbow: Bool

    var body: some View {
        HStack(spacing: Layout.swatchGap) {
            ForEach(0..<AppColors.presets.count, id: \.self) { index in
                let isSelected = selectedColorIndex == index

                RoundedRectangle(cornerRadius: Layout.swatchRadius)
                    .fill(AppColors.presets[index])
                    .frame(width: Layout.swatchSize, height: Layout.swatchSize)
                    .overlay {
                        if isSelected {
                            RoundedRectangle(cornerRadius: Layout.swatchRadius)
                                .stroke(Color.white, lineWidth: 2)
                        }
                    }
                    .scaleEffect(isSelected ? 1.1 : 1.0)
                    .opacity(isRainbow ? 0.45 : 1.0)
                    .animation(.spring(response: 0.25), value: isSelected)
                    .animation(.easeInOut(duration: 0.2), value: isRainbow)
                    .onTapGesture {
                        guard !isRainbow else { return }
                        selectedColorIndex = index
                        let gen = UISelectionFeedbackGenerator()
                        gen.prepare()
                        gen.selectionChanged()
                    }
            }

            Spacer()

            // Rainbow toggle inline
            Button {
                isRainbow.toggle()
                let gen = UISelectionFeedbackGenerator()
                gen.prepare()
                gen.selectionChanged()
            } label: {
                Text("🌈")
                    .font(.system(size: 20))
                    .frame(width: Layout.swatchSize, height: Layout.swatchSize)
                    .background(isRainbow
                        ? Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.6)
                        : Color(white: 0.18))
                    .clipShape(RoundedRectangle(cornerRadius: Layout.swatchRadius))
                    .overlay {
                        if isRainbow {
                            RoundedRectangle(cornerRadius: Layout.swatchRadius)
                                .stroke(Color.white, lineWidth: 2)
                        }
                    }
                    .scaleEffect(isRainbow ? 1.1 : 1.0)
                    .animation(.spring(response: 0.25), value: isRainbow)
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 5)
    }
}
