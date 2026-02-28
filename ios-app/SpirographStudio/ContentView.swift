import SwiftUI
import UIKit
import Photos

struct ContentView: View {

    // MARK: - Engine

    @StateObject private var engine: DrawingEngine = {
        let w = UIScreen.main.bounds.width
        return DrawingEngine(canvasSize: w)
    }()

    // MARK: - Slider State

    @State private var sliderR: Double     = 150
    @State private var sliderr: Double     = 80
    @State private var sliderd: Double     = 100
    @State private var sliderSpeed: Double = 5
    @State private var sliderWidth: Double = 1

    // MARK: - Color State

    @State private var selectedColorIndex: Int = 0
    @State private var isRainbow: Bool          = false

    // MARK: - UI State

    @State private var showToast:    Bool   = false
    @State private var toastMessage: String = ""
    @State private var lastPresetIndex: Int = -1
    @State private var showSaved:    Bool   = false
    @State private var showPermissionAlert: Bool = false

    // MARK: - Tutorial

    @AppStorage("hasSeenTutorial") private var hasSeenTutorial = false
    @State private var showTutorial = false

    // MARK: - Scene Phase

    @Environment(\.scenePhase) private var scenePhase

    // MARK: - Derived

    var effectiver: Double { min(sliderr, sliderR - 1) }

    var currentColorMode: ColorMode {
        if isRainbow { return .rainbow }
        return .solid(AppColors.presetsUI[selectedColorIndex])
    }

    var currentSwatchColor: Color {
        AppColors.presets[selectedColorIndex]
    }

    // MARK: - Body

    var body: some View {
        ZStack {
            AppColors.background.ignoresSafeArea()

            GeometryReader { geo in
                let availH = geo.size.height
                let availW = geo.size.width
                let canvasSz = min(availW, availH - 44 - Layout.controlsPanelHeight)

                VStack(spacing: 0) {
                    TitleBarView(isDrawing: engine.isDrawing, layerCount: engine.layerCount)
                        .frame(height: 44)

                    // Canvas area — fills remaining space between title and controls
                    ZStack {
                        AppColors.background

                        CanvasView(
                            engine: engine,
                            showToast: $showToast,
                            toastMessage: $toastMessage,
                            R: sliderR,
                            r: effectiver,
                            d: sliderd,
                            isRainbow: isRainbow,
                            selectedColor: currentSwatchColor
                        )
                        .frame(width: canvasSz, height: canvasSz)
                    }
                    .frame(width: availW,
                           height: availH - 44 - Layout.controlsPanelHeight)

                    // Controls panel — fixed height, no scroll
                    ControlsPanelView(
                        sliderR: $sliderR,
                        sliderr: $sliderr,
                        sliderd: $sliderd,
                        sliderSpeed: $sliderSpeed,
                        sliderWidth: $sliderWidth,
                        selectedColorIndex: $selectedColorIndex,
                        isRainbow: $isRainbow,
                        engine: engine,
                        onDraw:   handleDraw,
                        onUndo:   handleUndo,
                        onClear:  handleClear,
                        onRandom: handleRandom,
                        onSave:   handleSave
                    )
                    .frame(height: Layout.controlsPanelHeight)
                }
            }

            // Tutorial overlay
            if showTutorial {
                TutorialOverlayView(isPresented: $showTutorial)
                    .transition(.opacity)
                    .zIndex(10)
            }
        }
        .preferredColorScheme(.dark)
        .onAppear {
            if !hasSeenTutorial {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
                    withAnimation {
                        showTutorial = true
                    }
                }
            }
        }
        .onChange(of: showTutorial) { _, visible in
            if !visible {
                hasSeenTutorial = true
            }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .background {
                engine.stopDrawing()
            }
        }
        .alert("Photos Access Needed",
               isPresented: $showPermissionAlert) {
            Button("Open Settings") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Please allow Photos access in Settings to save your artwork.")
        }
    }

    // MARK: - Actions

    private func handleDraw() {
        engine.startDrawing(
            R: sliderR,
            r: effectiver,
            d: sliderd,
            speed: Int(sliderSpeed),
            lineWidth: sliderWidth,
            colorMode: currentColorMode
        )
    }

    private func handleUndo() {
        engine.undo()
    }

    private func handleClear() {
        engine.clear()
    }

    private func handleRandom() {
        let presets = SpiroPresets.curated
        var idx = Int.random(in: 0..<presets.count)
        if idx == lastPresetIndex && presets.count > 1 {
            idx = (idx + 1) % presets.count
        }
        lastPresetIndex = idx
        let preset = presets[idx]

        withAnimation(.easeInOut(duration: 0.4)) {
            sliderR = preset.R
            sliderr = preset.r
            sliderd = preset.d
        }

        showToastMessage("🎲 \(preset.name)")

        let gen = UIImpactFeedbackGenerator(style: .light)
        gen.prepare()
        gen.impactOccurred()
    }

    private func handleSave() {
        let image = engine.canvasImage

        let gen = UIImpactFeedbackGenerator(style: .medium)
        gen.prepare()
        gen.impactOccurred()

        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            DispatchQueue.main.async {
                if status == .authorized || status == .limited {
                    UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
                    showSavedFeedback()
                } else if status == .denied || status == .restricted {
                    showPermissionAlert = true
                }
                presentShareSheet(image: image)
            }
        }
    }

    private func presentShareSheet(image: UIImage) {
        let ac = UIActivityViewController(activityItems: [image], applicationActivities: nil)
        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let root = scene.windows.first?.rootViewController {
            root.present(ac, animated: true)
        }
    }

    private func showSavedFeedback() {
        showSaved = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            showSaved = false
        }
    }

    private func showToastMessage(_ message: String) {
        toastMessage = message
        withAnimation {
            showToast = true
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation {
                showToast = false
            }
        }
    }
}
