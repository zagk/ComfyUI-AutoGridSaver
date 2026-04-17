import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "AutoGridSaver.Buttons",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "AutoGridSaver") return;

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function() {
            if (originalOnNodeCreated) {
                originalOnNodeCreated.call(this);
            }

            // filename_prefix 위젯 찾기
            const filenameWidget = this.widgets.find(w => w.name === "filename_prefix");

            // ✅ Queue Grid 버튼만 유지
            const queueBtn = this.addWidget("button", "Queue Grid", "Queue", () => {
                const nImagesWidget = this.widgets.find(w => w.name === "n_images");
                const n = nImagesWidget ? nImagesWidget.value : 8;

                console.log(`AutoGridSaver: Queuing ${n} images...`);

                // N번 큐 추가 (한 장씩 생성)
                for (let i = 0; i < n; i++) {
                    app.queuePrompt(0, 1);
                }
            });

            // 버튼 위치 조정 (filename_prefix 아래)
            if (filenameWidget) {
                const idx = this.widgets.indexOf(filenameWidget);
                this.widgets.splice(idx + 1, 0, queueBtn);
            }
        };
    }
});