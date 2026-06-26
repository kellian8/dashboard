// The right-hand profit/loss column: total P/L over a divider, then the
// unrealized / realized split. Aligns to the top of the big total value.
import QtQuick
import QtQuick.Layouts

ColumnLayout {
    property string totalPl: "—"
    property color totalPlColor: "#999999"
    property string totalPlArrow: ""
    property string unrealizedPl: "—"
    property color unrealizedColor: "#999999"
    property string realizedPl: "—"
    property color realizedColor: "#999999"

    spacing: 0

    Text {
        text: "Total P/L " + totalPlArrow
        font.pixelSize: 10
        color: "#999999"
        bottomPadding: 2
    }
    Text {
        text: totalPl
        font.pixelSize: 13
        font.weight: Font.Medium
        color: totalPlColor
        bottomPadding: 6
    }

    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 1
        color: "#cccccc"
    }

    RowLayout {
        Layout.topMargin: 6
        spacing: 16

        ColumnLayout {
            spacing: 2
            Text { text: "Unrealized P/L"; font.pixelSize: 10; color: "#999999" }
            Text {
                text: unrealizedPl
                font.pixelSize: 11
                font.weight: Font.Medium
                color: unrealizedColor
            }
        }
        ColumnLayout {
            spacing: 2
            Text { text: "Realized P/L"; font.pixelSize: 10; color: "#999999" }
            Text {
                text: realizedPl
                font.pixelSize: 11
                font.weight: Font.Medium
                color: realizedColor
            }
        }
    }
}
