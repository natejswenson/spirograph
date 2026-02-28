import SwiftUI
import UIKit

enum AppColors {
    // Backgrounds
    static let background = Color(red: 0.071, green: 0.071, blue: 0.122)
    static let panel      = Color(red: 0.094, green: 0.094, blue: 0.157)

    // Canvas
    static let canvasBg           = Color(red: 0.047, green: 0.047, blue: 0.094)
    static let canvasDot          = Color(red: 0.200, green: 0.220, blue: 0.340)
    static let canvasAuraIdle     = Color(red: 0.300, green: 0.200, blue: 0.600).opacity(0.25)
    static let canvasAuraDrawing  = Color(red: 0.388, green: 0.400, blue: 0.945).opacity(0.55)

    // UI chrome
    static let title       = Color.white
    static let sliderTrack = Color(white: 0.18)
    static let sliderHandle = Color.white
    static let statusText  = Color(white: 0.55)
    static let cardBorder  = Color(white: 0.15)

    // Slider accent colors
    static let sliderR     = Color(red: 0.506, green: 0.549, blue: 0.973)
    static let sliderr     = Color(red: 0.984, green: 0.443, blue: 0.522)
    static let sliderd     = Color(red: 0.204, green: 0.827, blue: 0.600)
    static let sliderSpeed = Color(red: 0.984, green: 0.749, blue: 0.141)
    static let sliderWidth = Color(red: 0.655, green: 0.545, blue: 0.980)

    // Drawing color presets (8 swatches)
    static let presets: [Color] = [
        Color(red: 1.000, green: 1.000, blue: 1.000), // white
        Color(red: 0.976, green: 0.341, blue: 0.341), // red
        Color(red: 0.988, green: 0.588, blue: 0.216), // orange
        Color(red: 0.988, green: 0.843, blue: 0.118), // yellow
        Color(red: 0.235, green: 0.882, blue: 0.471), // green
        Color(red: 0.118, green: 0.824, blue: 0.961), // cyan
        Color(red: 0.412, green: 0.424, blue: 1.000), // blue
        Color(red: 0.910, green: 0.294, blue: 0.902), // magenta
    ]

    static let presetsUI: [UIColor] = [
        UIColor(red: 1.000, green: 1.000, blue: 1.000, alpha: 1),
        UIColor(red: 0.976, green: 0.341, blue: 0.341, alpha: 1),
        UIColor(red: 0.988, green: 0.588, blue: 0.216, alpha: 1),
        UIColor(red: 0.988, green: 0.843, blue: 0.118, alpha: 1),
        UIColor(red: 0.235, green: 0.882, blue: 0.471, alpha: 1),
        UIColor(red: 0.118, green: 0.824, blue: 0.961, alpha: 1),
        UIColor(red: 0.412, green: 0.424, blue: 1.000, alpha: 1),
        UIColor(red: 0.910, green: 0.294, blue: 0.902, alpha: 1),
    ]

    // Buttons
    static let btnDraw   = Color(red: 0.388, green: 0.400, blue: 0.945)
    static let btnUndo   = Color(red: 0.851, green: 0.467, blue: 0.024)
    static let btnClear  = Color(red: 0.863, green: 0.149, blue: 0.149)
    static let btnSave   = Color(red: 0.086, green: 0.639, blue: 0.290)
    static let btnRandom = Color(red: 0.400, green: 0.200, blue: 0.800)

    // Glassmorphism surfaces
    static let glassBorder    = Color.white.opacity(0.12)
    static let glassHighlight = Color.white.opacity(0.06)

    // Title bar pulsing dot
    static let dotDrawing = Color(red: 0.388, green: 0.400, blue: 0.945)
    static let dotIdle    = Color(red: 0.294, green: 0.247, blue: 0.541)
}
