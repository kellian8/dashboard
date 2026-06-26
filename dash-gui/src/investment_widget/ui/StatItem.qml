// A small labelled statistic, e.g. "LAST 24H" / "↙ £ 19.50".
import QtQuick
import QtQuick.Layouts

ColumnLayout {
    property string label: ""
    property string value: "—"
    property color valueColor: "#999999"

    spacing: 3

    Text {
        text: label
        font.pixelSize: 9
        font.letterSpacing: 0.4
        color: "#999999"
    }
    Text {
        text: value
        font.pixelSize: 11
        font.weight: Font.Medium
        color: valueColor
    }
}
