import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 521
    height: 140

    Rectangle {
        anchors.fill: parent
        radius: 12
        color: Qt.rgba(0.08, 0.08, 0.08, 0.88)

        // Draggable window
        MouseArea {
            id: dragArea
            anchors.fill: parent
            property point clickPos: Qt.point(0, 0)
            onPressed: (mouse) => { clickPos = Qt.point(mouse.x, mouse.y) }
            onPositionChanged: (mouse) => {
                var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
                bridge.moveWindow(delta.x, delta.y)
            }
        }

        Column {
            spacing: 8
            padding: 20

            Column {
                spacing: 15

                Text {
                    text: bridge ? bridge.investment_summary_label : ""
                    color: "white"
                    font.pixelSize: 16
                    font.weight: Font.Bold
                }

                Row {
                    spacing: 60

                    PortfolioSummaryKVColumn { fields: bridge ? bridge.investment_summary_fields : []; offset: 0 }

                    Rectangle {
                        width: 1
                        height: 65
                        anchors.verticalCenter: parent.verticalCenter
                        color: "#666666"
                    }

                    PortfolioSummaryKVColumn { fields: bridge ? bridge.investment_summary_fields: []; offset: 3 }
                }
            }
        }
    }
}
