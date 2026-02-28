import UIKit

enum ColorMode {
    case solid(UIColor)
    case rainbow

    func resolvedColor(index: Int, total: Int) -> UIColor {
        switch self {
        case .solid(let color):
            return color
        case .rainbow:
            let hue = CGFloat(index) / CGFloat(max(total, 1))
            return UIColor(hue: hue, saturation: 1.0, brightness: 1.0, alpha: 1.0)
        }
    }
}
