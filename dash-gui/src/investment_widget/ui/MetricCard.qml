// One of the three grey rounded cards along the bottom.
import QtQuick
import QtQuick.Layouts

Rectangle {
    property string label: ""
    property string value: "—"

    Layout.fillWidth: true
    implicitHeight: body.implicitHeight + 14
    radius: 8
    color: "#f5f5f5"

    ColumnLayout {
        id: body
        x: 10
        y: 7
        width: parent.width - 20
        spacing: 3

        Text {
            text: label
            font.pixelSize: 10
            color: "#666666"
        }
        Text {
            text: value
            font.pixelSize: 14
            font.weight: Font.Medium
            color: "#111111"
        }
    }
}
