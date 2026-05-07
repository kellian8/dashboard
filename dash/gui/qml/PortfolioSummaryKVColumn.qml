import QtQuick 2.15

Column {
    spacing: 6

    property var fields: []
    property int offset: 0

    Repeater {
        model: 3
        Item {
            width: 180
            height: 14
            Text {
                anchors.left: parent.left
                text: (offset + index) < fields.length ? fields[offset + index].key + ":" : ""
                color: "#aaaaaa"
                font.pixelSize: 14
                font.weight: Font.Medium
            }
            Text {
                anchors.right: parent.right
                text: {
                    var v = (offset + index) < fields.length ? fields[offset + index].value : ""
                    return v.replace("£", "<font color='#772418'>£</font>")
                }
                textFormat: Text.RichText
                color: "white"
                font.pixelSize: 14
            }
        }
    }
}
