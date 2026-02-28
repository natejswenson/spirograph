import Foundation

struct SpiroPreset {
    let R: Double
    let r: Double
    let d: Double
    let name: String
}

enum SpiroPresets {
    static let curated: [SpiroPreset] = [
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
}
