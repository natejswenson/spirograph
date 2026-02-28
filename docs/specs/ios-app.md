# Spirograph Studio — iOS App Specification

**Version:** 1.0
**Target:** iPhone (iOS 17+)
**Framework:** SwiftUI (native)
**Orientation:** Portrait only
**Monetization:** Free, no IAP
**Theme:** Single dark theme
**Audience:** Kids ages 6–18

---

## 1. Purpose & Context

Spirograph Studio is an interactive drawing app that lets users create mathematical hypotrochoid curves — the same patterns produced by a physical Spirograph toy. The user controls three geometric parameters (outer circle radius R, inner wheel radius r, pen distance d) plus speed and line width, then watches the curve animate onto a canvas in real time.

This spec converts the existing Python/Pygame desktop app into a native SwiftUI iPhone app with identical core math, all existing features, and additional iOS-native enhancements: share sheet, save to Photos, haptic feedback, a random-preset button, and a first-launch tutorial.

**Reference implementation:** `/Users/natejswenson/localrepo/spirograph/`
Key files: `spiro_math.py` (math), `pygame_app/drawing_engine.py` (rendering), `pygame_app/preview.py` (mechanism animation), `constants.py` (sizes), `theme.py` (colors).

---

## 2. Scope

### IN SCOPE
- All 5 parameter sliders (R, r, d, Speed, Line Width)
- 8 preset color swatches + Rainbow gradient mode
- Draw button with animated step-by-step curve rendering
- Undo (max 20 states) and Clear
- Layer stacking (multiple curves on one canvas)
- Animated mechanism preview widget (spinning outer ring + inner wheel + pen arm + ghost trace)
- Dot-grid background on canvas
- Progress indicator during drawing
- Random preset button (dice)
- Save to Photos
- Share Sheet (iOS native)
- Haptic feedback
- First-launch animated tutorial (skippable)
- Single dark theme

### OUT OF SCOPE
- iPad layout
- Landscape orientation
- In-app purchases
- User accounts / cloud sync
- TUI/terminal version
- Android build

---

## 3. Mathematical Core

### 3.1 Hypotrochoid Equations

```
x(t) = (R - r) * cos(t) + d * cos((R - r) * t / r)
y(t) = (R - r) * sin(t) - d * sin((R - r) * t / r)
```

- **R**: radius of the outer fixed circle
- **r**: radius of the inner rolling wheel (clamped: `r = min(r, R - 1)`)
- **d**: distance from center of inner wheel to the drawing pen
- **t**: parameter ranging from `0` to `2π × loops`

### 3.2 Period Calculation

```swift
func gcd(_ a: Int, _ b: Int) -> Int {
    b == 0 ? a : gcd(b, a % b)
}

let loops = r / gcd(R, r)   // number of inner wheel rotations to close the curve
let totalSteps = 6000        // fixed resolution for smooth curves
```

### 3.3 Point Generation

```swift
func computePoints(R: Double, r: Double, d: Double) -> [CGPoint] {
    let rClamped = min(r, R - 1)
    let loops = Int(rClamped) / gcd(Int(rClamped), Int(R))  // NOTE: gcd(R, r) not gcd(r, R) — see reference impl
    let steps = 6000
    var points: [CGPoint] = []
    for i in 0...steps {
        let t = 2.0 * .pi * Double(loops) * Double(i) / Double(steps)
        let x = (R - rClamped) * cos(t) + d * cos((R - rClamped) * t / rClamped)
        let y = (R - rClamped) * sin(t) - d * sin((R - rClamped) * t / rClamped)
        points.append(CGPoint(x: x, y: y))
    }
    return points
}
```

### 3.4 Point Scaling to Canvas

After generating raw points, scale and center them to fit the canvas:

```swift
func scalePoints(_ points: [CGPoint], canvasSize: CGFloat, margin: CGFloat) -> [CGPoint] {
    let maxExtent = points.map { max(abs($0.x), abs($0.y)) }.max() ?? 1
    let scale = (canvasSize / 2 - margin) / maxExtent
    let center = CGPoint(x: canvasSize / 2, y: canvasSize / 2)
    return points.map {
        CGPoint(x: center.x + $0.x * scale, y: center.y + $0.y * scale)
    }
}
```

Constants:
- `CANVAS_MARGIN = 28.0` (minimum padding from edge to curve extent)

---

## 4. Visual Design

### 4.1 Color Palette (Dark Theme — single theme, never changes)

```swift
enum AppColors {
    // Background
    static let background    = Color(red: 0.071, green: 0.071, blue: 0.122)  // #12122F dark navy
    static let panel         = Color(red: 0.094, green: 0.094, blue: 0.157)  // panel bg

    // Canvas
    static let canvasBg      = Color(red: 0.047, green: 0.047, blue: 0.094)  // very dark navy
    static let canvasDot     = Color(red: 0.200, green: 0.220, blue: 0.340)  // subtle blue-gray dots
    static let canvasAuraIdle    = Color(indigo: true, alpha: 0.25)          // muted purple glow at rest
    static let canvasAuraDrawing = Color(indigo: true, alpha: 0.55)          // stronger indigo glow while drawing

    // UI chrome
    static let title         = Color.white
    static let sliderTrack   = Color(white: 0.18)
    static let sliderHandle  = Color.white
    static let statusText    = Color(white: 0.55)

    // Slider accent colors (match desktop app)
    static let sliderR       = Color(red: 0.506, green: 0.549, blue: 0.973)  // lavender #818CF8
    static let sliderr       = Color(red: 0.984, green: 0.443, blue: 0.522)  // pink #FB7185
    static let sliderd       = Color(red: 0.204, green: 0.827, blue: 0.600)  // mint #34D399
    static let sliderSpeed   = Color(red: 0.984, green: 0.749, blue: 0.141)  // amber #FBD024
    static let sliderWidth   = Color(red: 0.655, green: 0.545, blue: 0.980)  // purple #A78BFA

    // Drawing colors (8 presets — exact RGB from desktop)
    static let presets: [Color] = [
        Color(red: 1.000, green: 1.000, blue: 1.000),  // white
        Color(red: 0.976, green: 0.341, blue: 0.341),  // red    #F95757
        Color(red: 0.988, green: 0.588, blue: 0.216),  // orange #FC9637
        Color(red: 0.988, green: 0.843, blue: 0.118),  // yellow #FCDB1E
        Color(red: 0.235, green: 0.882, blue: 0.471),  // green  #3CE178
        Color(red: 0.118, green: 0.824, blue: 0.961),  // cyan   #1ED2F5
        Color(red: 0.412, green: 0.424, blue: 1.000),  // blue   #696CFF
        Color(red: 0.910, green: 0.294, blue: 0.902),  // magenta#E84BE6
    ]

    // Buttons
    static let btnDraw   = Color(red: 0.388, green: 0.400, blue: 0.945)  // indigo  #636EF1
    static let btnUndo   = Color(red: 0.851, green: 0.467, blue: 0.024)  // amber   #D97718
    static let btnClear  = Color(red: 0.863, green: 0.149, blue: 0.149)  // red     #DC2626
    static let btnSave   = Color(red: 0.086, green: 0.639, blue: 0.290)  // green   #16A34A
    static let btnRandom = Color(red: 0.400, green: 0.200, blue: 0.800)  // purple  #6633CC
}
```

### 4.2 Typography

```swift
// Title
Font.system(size: 22, weight: .bold, design: .rounded)   // "Spirograph Studio ✦"

// Slider labels
Font.system(size: 13, weight: .medium, design: .rounded)

// Slider values
Font.system(size: 13, weight: .semibold, design: .monospaced)

// Button labels
Font.system(size: 15, weight: .bold, design: .rounded)

// Status bar
Font.system(size: 11, weight: .regular, design: .monospaced)

// Section headers
Font.system(size: 11, weight: .semibold, design: .rounded).uppercaseSmallCaps()
```

### 4.3 Corner Radii & Spacing

```swift
enum Layout {
    static let cardRadius: CGFloat    = 16
    static let buttonRadius: CGFloat  = 12
    static let swatchRadius: CGFloat  = 8
    static let swatchSize: CGFloat    = 32
    static let swatchGap: CGFloat     = 8
    static let cardPadding: CGFloat   = 14
    static let sectionGap: CGFloat    = 10
    static let sliderHeight: CGFloat  = 6   // track thickness
    static let sliderThumbSize: CGFloat = 22
}
```

---

## 5. Layout Architecture (Portrait iPhone)

### 5.1 Overall Structure

```
┌─────────────────────────────┐
│  Status Bar (system)        │
├─────────────────────────────┤
│  Title Bar                  │  44pt
├─────────────────────────────┤
│                             │
│       CANVAS                │  Square, fills width (e.g. 390pt on iPhone 15)
│       (dot-grid bg)         │
│       (aura glow border)    │
│                             │
├─────────────────────────────┤
│  ┌──────────────────────┐   │
│  │ Mechanism Preview    │   │  130pt tall card
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │ Sliders (5×)         │   │  240pt tall card (48pt × 5)
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │ Color Picker         │   │  80pt tall card
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │ Buttons              │   │  140pt tall card
│  └──────────────────────┘   │
│  Status bar (text)          │  28pt
└─────────────────────────────┘
```

### 5.2 Canvas

- **Size:** Square, width = `UIScreen.main.bounds.width` (full width)
- **Background:** Dark navy + dot grid (see §7.2)
- **Aura:** Soft glow border (8pt blur, color transitions from idle to drawing state)
- **Content:** Rendered curve layers, accumulated on an offscreen `CGContext` / `UIImage`

### 5.3 Controls Area (ScrollView)

Wrap the controls area in a `ScrollView` so very small iPhones (SE) can scroll to access all controls. On larger iPhones (Pro Max), controls fit without scrolling.

Order (top to bottom):
1. Mechanism Preview card
2. Sliders card
3. Color Picker card
4. Buttons card
5. Status text

---

## 6. Screen & View Hierarchy

```
SpirographApp
└── ContentView
    ├── VStack
    │   ├── TitleBarView
    │   ├── CanvasView (square)
    │   └── ScrollView
    │       └── VStack
    │           ├── PreviewCard
    │           │   └── MechanismPreviewView (Canvas / TimelineView)
    │           ├── SlidersCard
    │           │   ├── SpiroSliderView (R)
    │           │   ├── SpiroSliderView (r)
    │           │   ├── SpiroSliderView (d)
    │           │   ├── SpiroSliderView (Speed)
    │           │   └── SpiroSliderView (Line Width)
    │           ├── ColorPickerCard
    │           │   ├── HStack (8 swatches)
    │           │   └── RainbowToggle
    │           ├── ButtonsCard
    │           │   ├── DrawButton (full width)
    │           │   ├── HStack
    │           │   │   ├── UndoButton
    │           │   │   └── ClearButton
    │           │   ├── HStack
    │           │   │   ├── RandomButton
    │           │   │   └── SaveButton
    │           └── StatusBarView
    └── TutorialOverlayView (shown on first launch, full-screen overlay)
```

---

## 7. Component Specifications

### 7.1 TitleBarView

```
┌─ ● Spirograph Studio ✦ ──────────────────┐
```

- Pulsing dot (●) on the left: indigo (#636EF1) when drawing, dim purple (#4B3F8A) when idle. Animate with `withAnimation(.easeInOut(duration: 0.8).repeatForever(autoreverses: true))` — scale between 0.7 and 1.0 while drawing.
- Title text: "Spirograph Studio ✦" in rounded bold.
- Background: `AppColors.panel` with bottom border 1pt at `Color(white: 0.15)`.
- Height: 44pt.

### 7.2 CanvasView

**State:** Renders an accumulated `UIImage` that persists across frames.

**Background (dot grid):**
```swift
func makeCanvasBackground(size: CGSize) -> UIImage {
    // Draw dark navy base
    // Draw dot grid: spacing = 28pt, dot radius = 1.2pt
    // Dot color varies: mix of canvasDot with slight brightness variation (±15%)
    // Dots near center slightly brighter for subtle vignette effect
    // Return as UIImage
}
```

**Aura Glow:**
- Implement as a `RoundedRectangle` overlay with `.shadow(color: auraColor, radius: 12)` that covers the canvas border.
- `auraColor` = `AppColors.canvasAuraDrawing` when drawing, `AppColors.canvasAuraIdle` when idle.
- Animate with `.animation(.easeInOut(duration: 0.4))`.

**Drawing Surface:**
- Maintain a `UIImage` property in `DrawingEngine` (the canvas state).
- Display it in SwiftUI via `Image(uiImage: canvasImage)`.
- Use `GeometryReader` to get exact display size.

**No interactive gestures on the canvas.** It is display-only.

### 7.3 MechanismPreviewView

This is an animated diagram showing the spirograph mechanism. It lives in its own card above the sliders.

**Size:** Fills the preview card width. Aspect ratio 1:1. Suggested height: 130pt.

**Implementation:** Use SwiftUI `Canvas` + `TimelineView(.animation)` for smooth 60fps animation.

**Animation state:** Angle `θ` increments each frame:
- Idle (not drawing): `θ += 0.018` radians/frame
- Drawing: `θ += 0.055` radians/frame

**What to draw (all coordinates relative to center of preview canvas):**

```
Let sz = min(previewWidth, previewHeight)
Let scale = sz / 2 * 0.82   // outer circle fits inside preview with padding
Let R_px = scale             // outer ring pixel radius
Let r_px = R_px * (r / R)   // inner wheel pixel radius
Let d_px = R_px * (d / R)   // pen arm pixel length

Center of outer circle: (sz/2, sz/2)
Center of inner wheel: (sz/2 + (R_px - r_px) * cos(θ),
                        sz/2 + (R_px - r_px) * sin(θ))
Pen position:          wheelCenter + d_px * (cos(-(R_px - r_px)/r_px * θ),
                                             sin(-(R_px - r_px)/r_px * θ))
```

**Draw in this order:**
1. **Ghost trace:** Full spirograph curve at 10% opacity (900 steps). Color = current drawing color (or white if rainbow). This gives user a preview of what they'll draw.
2. **Outer ring:** Circle outline, 2pt stroke, `AppColors.sliderR` (lavender), no fill.
3. **12 tick marks:** Radial lines at R_px, length 5pt, same color, rotated at 30° increments.
4. **Inner wheel:** Circle outline, 2pt stroke, `AppColors.sliderr` (pink), semi-transparent fill (30% opacity).
5. **4–8 gear dots on wheel perimeter:** Dots spaced evenly around wheel circumference. Radius 2pt. Pink.
6. **Crosshair through wheel center:** Horizontal + vertical lines, 4pt long each side, muted purple.
7. **Pen arm:** Line from wheel center to pen position. `AppColors.sliderd` (mint), 1.5pt, 80% opacity.
8. **Pen dot:** 3 concentric circles at pen position:
   - Outer: 5pt radius, current drawing color, 90% opacity
   - Middle: 3pt radius, white, 100% opacity
   - Inner: 2pt radius, current drawing color, 100% opacity
9. **Labels:** "R=\(Int(R))" near top-left, "r=\(Int(r))" near top-right. Font size 10, color `AppColors.statusText`.

**IMPORTANT:** Never mix global and local coordinates. All preview drawing uses local coordinates within the preview canvas (0,0) to (sz, sz).

### 7.4 SpiroSliderView

Each slider row contains:
```
┌─────────────────────────────────────┐
│  ⭕ Big Circle (R)            150   │
│  ══════════════●────────────        │  (track with thumb)
└─────────────────────────────────────┘
```

**Props:**
```swift
struct SpiroSliderView: View {
    let emoji: String
    let label: String
    var value: Binding<Double>
    let min: Double
    let max: Double
    let accentColor: Color
    // height: 48pt per row
}
```

**Slider parameters:**

| # | Emoji | Label | Min | Max | Default | Accent |
|---|-------|-------|-----|-----|---------|--------|
| 0 | ⭕ | Big Circle (R) | 50 | 300 | 150 | sliderR (lavender) |
| 1 | 🔵 | Little Wheel (r) | 5 | 200 | 80 | sliderr (pink) |
| 2 | ✏️ | Pen Reach (d) | 5 | 250 | 100 | sliderd (mint) |
| 3 | ⚡ | Speed | 1 | 20 | 5 | sliderSpeed (amber) |
| 4 | 📏 | Line Width | 1 | 8 | 1 | sliderWidth (purple) |

**Implementation:**
- Use `.init(_:in:step:)` with `step: 1.0` for integer-like behavior.
- Replace default SwiftUI Slider appearance: custom track (height 6pt, `AppColors.sliderTrack`), filled portion from leading edge to thumb in `accentColor`. Custom thumb: white circle 22pt diameter with 1pt shadow.
- Value label on the right: shows `Int(value)` for all sliders. Monospaced. Color = `accentColor`.
- Whole row height: 48pt.

### 7.5 ColorPickerCard

```
┌──── DRAW COLOR ─────────────────────┐
│  ⬤  ⬤  ⬤  ⬤  ⬤  ⬤  ⬤  ⬤       │  (8 swatches)
│  ◯ 🌈 Rainbow                       │  (toggle)
└─────────────────────────────────────┘
```

**8 swatches:**
- Size: 32×32pt each, `swatchRadius = 8pt`
- Gap: 8pt between swatches
- Selected swatch: 3pt white border ring + slight scale up (1.15×)
- Unselected: no border, scale 1.0
- Animate selection change with `.animation(.spring(response: 0.25))`

**Rainbow toggle:**
- `Toggle("🌈 Rainbow", isOn: $isRainbow)`
- Custom toggle style matching dark theme
- When rainbow is ON, all 8 swatches dim to 50% opacity
- When rainbow is ON, disable swatch taps (or gray them out)

**State:** `@State var selectedColorIndex: Int = 0` and `@State var isRainbow: Bool = false`

### 7.6 Buttons Card

```
┌─────────────────────────────────────┐
│  [      ▶  Draw         ]           │  full width, indigo
│  [ ↩ Undo ]   [ ✕ Clear ]          │  split width, amber + red
│  [ 🎲 Random ] [ 💾 Save ]          │  split width, purple + green
└─────────────────────────────────────┘
```

**Button heights:** 44pt each, 8pt gap between rows.

**Button states:**

- **Draw:** Label = "▶  Draw" normally. When drawing: label = "⏹  XX%" where XX is draw progress 0–100. Background stays indigo but slightly dimmer during drawing. Tapping Draw while drawing cancels the animation.
- **Undo:** Disabled (50% opacity) when undo stack is empty.
- **Clear:** Always enabled. Shows confirmation via haptic (no dialog — just clear immediately).
- **Random:** Picks a visually interesting parameter combination (see §8.4). Purple background.
- **Save:** Presents iOS share sheet AND saves to Photos simultaneously. Green background.

**Button style:**
```swift
struct SpiroButton: ButtonStyle {
    let color: Color
    let isDisabled: Bool

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .frame(maxWidth: .infinity)
            .frame(height: 44)
            .background(color.opacity(configuration.isPressed ? 0.75 : (isDisabled ? 0.4 : 1.0)))
            .cornerRadius(12)
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}
```

### 7.7 StatusBarView

Single line of monospaced text at the bottom:

- **While drawing:** `"R=\(R)  r=\(r)  d=\(d)  ·  Drawing \(progress)%  ·  \(layerCount) layers"`
- **After save:** `"✓ Saved  ·  \(layerCount) layers"` (show for 2 seconds, then revert)
- **Idle:** `"R=\(R)  r=\(r)  d=\(d)  ·  \(layerCount) layers  ·  undo: \(undoCount)"`

Color: `AppColors.statusText`. Font: monospaced 11pt.

---

## 8. Feature Specifications

### 8.1 Drawing Engine

**Storage:** `DrawingEngine` is an `ObservableObject` that owns:

```swift
class DrawingEngine: ObservableObject {
    @Published var canvasImage: UIImage        // current canvas (all layers)
    @Published var isDrawing: Bool = false
    @Published var drawProgress: Double = 0.0  // 0.0 – 1.0
    @Published var layerCount: Int = 0

    private var undoStack: [UIImage] = []      // max 20
    private let maxUndo = 20
    private var drawPoints: [CGPoint] = []
    private var drawIndex: Int = 0
    private var drawTimer: Timer?

    let canvasSize: CGFloat                    // set at init

    // ...methods below
}
```

**Canvas initialization:**
```swift
init(canvasSize: CGFloat) {
    self.canvasSize = canvasSize
    self.canvasImage = makeBackground(size: CGSize(width: canvasSize, height: canvasSize))
}
```

**Drawing animation (timer-based):**
```swift
func startDrawing(R: Double, r: Double, d: Double, speed: Int, lineWidth: Double,
                  colorMode: ColorMode, solidColor: UIColor) {
    guard !isDrawing else { stopDrawing(); return }

    pushUndo()

    let rawPoints = computePoints(R: R, r: r, d: d)   // 6001 points
    drawPoints = scalePoints(rawPoints, canvasSize: canvasSize, margin: 28)
    drawIndex = 1
    isDrawing = true
    layerCount += 1

    // Fire timer at 60fps, advance `speed` segments per tick
    drawTimer = Timer.scheduledTimer(withTimeInterval: 1.0/60.0, repeats: true) { [weak self] _ in
        self?.stepDraw(steps: speed, lineWidth: lineWidth, colorMode: colorMode, solidColor: solidColor)
    }
}

private func stepDraw(steps: Int, lineWidth: Double, colorMode: ColorMode, solidColor: UIColor) {
    guard isDrawing, drawIndex < drawPoints.count else {
        stopDrawing()
        return
    }

    let end = min(drawIndex + steps, drawPoints.count - 1)

    UIGraphicsBeginImageContextWithOptions(CGSize(width: canvasSize, height: canvasSize), true, 1.0)
    canvasImage.draw(at: .zero)

    let ctx = UIGraphicsGetCurrentContext()!
    ctx.setLineWidth(lineWidth)
    ctx.setLineCap(.round)
    ctx.setLineJoin(.round)

    for i in drawIndex..<end {
        let color = resolvedColor(mode: colorMode, solid: solidColor, index: i, total: drawPoints.count)
        ctx.setStrokeColor(color.cgColor)
        ctx.move(to: drawPoints[i - 1])
        ctx.addLine(to: drawPoints[i])
        ctx.strokePath()
    }

    canvasImage = UIGraphicsGetImageFromCurrentImageContext()!
    UIGraphicsEndImageContext()

    drawIndex = end
    drawProgress = Double(drawIndex) / Double(drawPoints.count - 1)
}

func stopDrawing() {
    drawTimer?.invalidate()
    drawTimer = nil
    isDrawing = false
    drawProgress = 0
}
```

**Color resolution:**
```swift
enum ColorMode {
    case solid(UIColor)
    case rainbow
}

func resolvedColor(mode: ColorMode, solid: UIColor, index: Int, total: Int) -> UIColor {
    switch mode {
    case .solid(let c): return c
    case .rainbow:
        let hue = CGFloat(index) / CGFloat(total)
        return UIColor(hue: hue, saturation: 1.0, brightness: 1.0, alpha: 1.0)
    }
}
```

### 8.2 Undo System

```swift
func pushUndo() {
    undoStack.append(canvasImage)
    if undoStack.count > maxUndo {
        undoStack.removeFirst()
    }
}

func undo() {
    guard !undoStack.isEmpty else { return }
    stopDrawing()
    canvasImage = undoStack.removeLast()
    layerCount = max(0, layerCount - 1)
}

func clear() {
    pushUndo()
    canvasImage = makeBackground(size: CGSize(width: canvasSize, height: canvasSize))
    layerCount = 0
}

var canUndo: Bool { !undoStack.isEmpty }
var undoCount: Int { undoStack.count }
```

### 8.3 Save & Share

```swift
func saveAndShare(from viewController: UIViewController) {
    let image = engine.canvasImage

    // 1. Save to Photos
    PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
        if status == .authorized || status == .limited {
            UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
        }
    }

    // 2. Show share sheet
    DispatchQueue.main.async {
        let ac = UIActivityViewController(activityItems: [image], applicationActivities: nil)
        viewController.present(ac, animated: true)

        // Haptic feedback
        let feedback = UIImpactFeedbackGenerator(style: .medium)
        feedback.impactOccurred()
    }
}
```

**Info.plist key required:**
```xml
<key>NSPhotoLibraryAddUsageDescription</key>
<string>Spirograph Studio saves your artwork to Photos so you can share it.</string>
```

**Note:** The app does NOT save to `~/Desktop`. It saves to the iOS Photos library and shares via the native share sheet.

### 8.4 Random Preset Button

Pre-define a curated list of parameter combinations known to produce beautiful spirographs. On tap, pick one at random (never repeat the same one consecutively).

```swift
struct SpiroPreset {
    let R: Double, r: Double, d: Double
    let name: String
}

let curated: [SpiroPreset] = [
    SpiroPreset(R: 150, r: 80,  d: 100, name: "Classic"),
    SpiroPreset(R: 200, r: 130, d: 150, name: "Star"),
    SpiroPreset(R: 180, r: 45,  d: 120, name: "Petal"),
    SpiroPreset(R: 150, r: 60,  d: 60,  name: "Rose"),
    SpiroPreset(R: 200, r: 70,  d: 190, name: "Infinity"),
    SpiroPreset(R: 120, r: 55,  d: 80,  name: "Snowflake"),
    SpiroPreset(R: 175, r: 25,  d: 140, name: "Ring"),
    SpiroPreset(R: 200, r: 110, d: 200, name: "Galaxy"),
    SpiroPreset(R: 160, r: 48,  d: 110, name: "Web"),
    SpiroPreset(R: 190, r: 95,  d: 90,  name: "Diamond"),
    SpiroPreset(R: 145, r: 29,  d: 145, name: "Mandala"),
    SpiroPreset(R: 200, r: 150, d: 100, name: "Spiral"),
]
```

**Behavior:**
1. Pick random preset (exclude last used).
2. Animate slider values to new values using `withAnimation(.easeInOut(duration: 0.4))`.
3. Show preset name as a brief toast (see §8.6) e.g. "🎲 Petal".
4. Light haptic: `UIImpactFeedbackGenerator(style: .light).impactOccurred()`.

### 8.5 Haptic Feedback

| Event | Haptic Style |
|-------|-------------|
| Draw complete (animation finishes) | `.light` |
| Save button tapped | `.medium` |
| Random button tapped | `.light` |
| Clear button tapped | `.rigid` (sharp, destructive feel) |
| Undo button tapped | `.soft` |
| Swatch selected | `.selection` (`UISelectionFeedbackGenerator`) |
| Tutorial step advance | `.light` |

Always call `generator.prepare()` before `generator.impactOccurred()` for minimum latency.

### 8.6 Toast Notifications

Small floating toast for transient messages (save confirmation, random preset name):

```swift
struct ToastView: View {
    let message: String

    var body: some View {
        Text(message)
            .font(.system(size: 14, weight: .semibold, design: .rounded))
            .foregroundColor(.white)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(Color.black.opacity(0.75))
            .cornerRadius(20)
    }
}
```

Display: overlay at top of canvas area. Animate in with `.opacity` + `.offset(y: -10)` transition. Auto-dismiss after 1.5 seconds.

### 8.7 First-Launch Tutorial

**Trigger:** `@AppStorage("hasSeenTutorial") var hasSeenTutorial: Bool = false`. Show tutorial if `!hasSeenTutorial`.

**Implementation:** Full-screen sheet or overlay (`ZStack` over `ContentView`) with 4 steps.

**Tutorial steps (4 screens):**

```
Step 1: "What is a Spirograph?"
  - Animated mini spirograph drawing itself (use DrawingEngine on a small 200pt canvas)
  - Text: "A spirograph makes beautiful mathematical patterns — just like the toy!"
  - Background: dark with confetti particles (simple colored dots floating up)

Step 2: "Adjust the wheels"
  - Arrow pointing to slider area
  - Animated hand icon dragging a slider left and right
  - Text: "Drag the sliders to change the size of the circles and where the pen is."
  - Highlight: Sliders card glows with a subtle yellow outline

Step 3: "Pick a color & draw!"
  - Arrow pointing to color swatches
  - Then arrow pointing to Draw button
  - Text: "Pick your favorite color, then tap Draw to watch the magic happen! ✨"
  - Highlight: Color swatches animate (slight wiggle), then Draw button pulses

Step 4: "Save & share"
  - Arrow pointing to Save button
  - Text: "When you're done, save your artwork or share it with friends! 🎨"
  - Highlight: Save button glows green

Navigation:
  - Previous / Next buttons
  - "Skip" button top-right (always visible)
  - Page dots indicator (4 dots)
  - Final page "Next" becomes "Let's Go! 🚀"

On complete: set `hasSeenTutorial = true`, dismiss with scale + fade out animation.
```

---

## 9. State Management

Use a single `@StateObject` at the `ContentView` level:

```swift
@StateObject private var engine = DrawingEngine(canvasSize: UIScreen.main.bounds.width)
@State private var sliderR: Double = 150
@State private var sliderr: Double = 80
@State private var sliderd: Double = 100
@State private var sliderSpeed: Double = 5
@State private var sliderWidth: Double = 1
@State private var selectedColor: Int = 0    // index into AppColors.presets
@State private var isRainbow: Bool = false
@State private var showToast: Bool = false
@State private var toastMessage: String = ""
@State private var lastPresetIndex: Int = -1
```

**Derived value (never a stored state):**
```swift
var effectiveR: Double { min(sliderr, sliderR - 1) }
```

**Pass to DrawingEngine via method calls, not bindings.** Do not expose `DrawingEngine` internals as view state.

---

## 10. File Structure

```
SpiographStudio/
├── SpiographStudioApp.swift          // @main, app entry point
├── ContentView.swift                 // root layout, state ownership
├── Math/
│   └── SpiroMath.swift               // computePoints(), gcd(), scalePoints()
├── Engine/
│   └── DrawingEngine.swift           // ObservableObject, canvas, undo, draw loop
├── Views/
│   ├── TitleBarView.swift
│   ├── CanvasView.swift
│   ├── MechanismPreviewView.swift
│   ├── SlidersCard.swift
│   ├── SpiroSliderView.swift
│   ├── ColorPickerCard.swift
│   ├── ButtonsCard.swift
│   ├── StatusBarView.swift
│   └── ToastView.swift
├── Tutorial/
│   └── TutorialOverlayView.swift     // full tutorial flow
├── Models/
│   ├── ColorMode.swift               // enum { solid(UIColor), rainbow }
│   └── SpiroPreset.swift             // struct + curated list
├── Theme/
│   ├── AppColors.swift               // all Color constants
│   └── AppFonts.swift                // font helpers
└── Resources/
    └── Info.plist                    // NSPhotoLibraryAddUsageDescription
```

**Project name:** `SpirographStudio`
**Bundle ID:** `com.spirographstudio.app` (or developer's reverse domain)
**Minimum deployment target:** iOS 17.0
**Swift version:** Swift 5.9+

---

## 11. Constraints & Rules

### ALWAYS
- Clamp `r` to `min(r, R - 1)` before any math computation
- Use `UIGraphicsBeginImageContextWithOptions` with `scale: 1.0` (not display scale) for the drawing canvas so pixel coordinates are 1:1 with point coordinates
- Run drawing timer on `RunLoop.main` with `.common` mode so it fires during scroll
- Dismiss tutorial with animation (never just `isPresented = false` with no transition)
- Request Photos permission with `.addOnly` authorization (not full library access)
- Add `@MainActor` to all `DrawingEngine` published property updates that trigger UI redraws

### NEVER
- Never use `async/await` for the draw loop — use `Timer` for consistent 60fps
- Never store `UIImage` duplicates in the undo stack for more than 20 states
- Never block the main thread during point computation (6000 points is fast enough synchronously; no need for background thread)
- Never use `GeometryReader` inside a `ScrollView` for the canvas size — measure canvas size once at init via `UIScreen.main.bounds.width`
- Never show the iOS system color picker — use the custom 8-swatch picker only
- Never scale canvas content between layers (always use the same coordinate space)
- Never use `UIKit` view controllers directly in SwiftUI except for the share sheet presentation

### Performance
- Drawing timer: 60fps with `speed` segments per frame (5–100 line segments/frame)
- Canvas image updates: use `UIGraphicsBeginImageContextWithOptions` (not `UIGraphicsImageRenderer`) to avoid anti-aliasing overhead on the draw loop
- Preview animation: 60fps via `TimelineView(.animation)` — do NOT use Timer for this
- Undo stack images are full-size; 20 × ~1MB = ~20MB RAM budget acceptable on iPhone

---

## 12. Edge Cases

| Case | Handling |
|------|----------|
| `r >= R` | Clamp `r = R - 1` silently; slider UI still shows the raw slider value |
| `r = 0` | Should never happen (slider min = 5) but guard: if r < 1, r = 1 |
| `gcd(R, r) = 0` | Guard against; fallback loops = 1 |
| Tap Draw while drawing | Stop current animation immediately, do NOT start a new one |
| Undo stack empty | Undo button disabled (50% opacity), tapping does nothing |
| Photos permission denied | Show alert: "Please allow Photos access in Settings to save your artwork." |
| Very small iPhone (SE 1st gen, 320pt wide) | ScrollView ensures controls are reachable |
| App backgrounded during drawing | Pause timer in `scenePhase == .background`, resume on `.active` |
| Device rotation (landscape attempted) | Suppress — `UIInterfaceOrientationMask` = `.portrait` in `Info.plist` |

---

## 13. Permissions & App Store

### Info.plist entries required

```xml
<!-- Photos write -->
<key>NSPhotoLibraryAddUsageDescription</key>
<string>Spirograph Studio saves your artwork to your Photos library.</string>

<!-- Portrait orientation lock -->
<key>UISupportedInterfaceOrientations</key>
<array>
    <string>UIInterfaceOrientationPortrait</string>
</array>
```

### App Store metadata (suggested)

- **Name:** Spirograph Studio
- **Category:** Education (Primary), Entertainment (Secondary)
- **Age Rating:** 4+ (no objectionable content)
- **Keywords:** spirograph, drawing, kids, math, patterns, art, geometry, hypotrochoid

---

## 14. Testing Criteria

### Unit Tests (XCTest)

```swift
// SpiroMathTests.swift
func testGCD() {
    XCTAssertEqual(gcd(150, 80), 10)
    XCTAssertEqual(gcd(80, 150), 10)  // order-independent
    XCTAssertEqual(gcd(7, 3), 1)
}

func testLoops() {
    // loops = r / gcd(R, r) = 80 / gcd(150, 80) = 80 / 10 = 8
    XCTAssertEqual(computeLoops(R: 150, r: 80), 8)
}

func testPointCount() {
    let pts = computePoints(R: 150, r: 80, d: 100)
    XCTAssertEqual(pts.count, 6001)
}

func testRClamping() {
    let pts = computePoints(R: 100, r: 100, d: 50)  // r == R, should clamp
    XCTAssertNotNil(pts)  // no crash, no NaN
    XCTAssertFalse(pts.contains { $0.x.isNaN || $0.y.isNaN })
}

func testPointsAreCentered() {
    let pts = computePoints(R: 150, r: 80, d: 100)
    let scaled = scalePoints(pts, canvasSize: 390, margin: 28)
    let xs = scaled.map { $0.x }
    let ys = scaled.map { $0.y }
    // Max extent should not exceed canvas bounds
    XCTAssertTrue(xs.max()! <= 390 - 28)
    XCTAssertTrue(xs.min()! >= 28)
}
```

### UI Acceptance Criteria

- [ ] App launches and shows tutorial on first launch
- [ ] Tutorial has 4 steps, Skip and navigation work
- [ ] After tutorial, `hasSeenTutorial = true` (tutorial never shows again)
- [ ] Mechanism preview animates at ~0.018 rad/frame idle, ~0.055 rad/frame drawing
- [ ] All 5 sliders drag smoothly, values update in real time
- [ ] Color swatches: tapping selects with animation, only one selected at a time
- [ ] Rainbow toggle: swatches dim when on, rainbow gradient applies to next draw
- [ ] Draw button starts animated drawing; label shows progress %
- [ ] Tapping Draw while drawing stops animation
- [ ] Undo button restores previous canvas state; disabled when stack empty
- [ ] Clear resets canvas to background + dot grid; preserves undo state
- [ ] Multiple draws stack without clearing previous layers
- [ ] Random button animates sliders to new values and shows preset name toast
- [ ] Save button: Photos permission prompt on first use; saves image to Photos; share sheet appears
- [ ] Save haptic (medium) fires on Save
- [ ] Draw-complete haptic (light) fires when animation finishes naturally
- [ ] Status bar updates: shows R/r/d and layer count at all times
- [ ] Canvas aura glows brighter during drawing, dims when idle
- [ ] Title dot pulses while drawing
- [ ] On iPhone SE, all controls reachable by scrolling

---

## 15. Success Criteria

The implementation is complete when:

1. **Math correct:** Spirographs match the desktop app exactly for the same R, r, d values
2. **Smooth animation:** Drawing animation runs at 60fps with no stuttering
3. **Persistent layers:** Multiple spiral layers accumulate correctly without prior layers disappearing
4. **Undo works:** Up to 20 undo states restore the canvas correctly
5. **Preview accurate:** The mechanism preview reflects current slider values and animates continuously
6. **Share & Save work:** Photos save and share sheet function with correct permission handling
7. **Tutorial complete:** 4-step tutorial shows on first launch only, is fully skippable
8. **Random presets:** All 12 curated presets produce visually beautiful spirographs
9. **No crashes:** App handles all edge cases (r ≥ R, empty undo, Photos denied) without crashing
10. **Kid-friendly:** UI is large-touch-target friendly (all buttons ≥ 44pt), colorful, and engaging

---

## 16. Reference: Desktop App Parameters

When in doubt, the desktop app at `/Users/natejswenson/localrepo/spirograph/` is the ground truth for:
- Math implementation: `spiro_math.py`
- Color values: `theme.py`
- Canvas size and margin constants: `constants.py`
- Drawing animation logic: `pygame_app/drawing_engine.py`
- Preview widget behavior: `pygame_app/preview.py`

Key constants to match:
- Canvas size: 680px on desktop → use full iPhone screen width on iOS (dynamically sized)
- `CANVAS_MARGIN = 28` (in display points, not pixels)
- `steps = 6000` for point generation
- Max undo: 20 states
- Speed slider maps to `speed` line segments drawn per frame (not multiplied by 5 as in desktop)
