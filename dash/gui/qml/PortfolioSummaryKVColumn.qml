import QtQuick 2.15

Column {
    spacing: 6

    property var fields: []
    property int offset: 0

    Repeater {
        model: 4
        Item {
            width: 150
            height: 14
            Text {
                anchors.left: parent.left
                text: fields[offset + index].key + ":"
                color: "#aaaaaa"
                font.pixelSize: 14
                font.weight: Font.Medium
            }
            Text {
                anchors.right: parent.right
                text: fields[offset + index].value
                color: "white"
                font.pixelSize: 14
            }
        }
    }
}
