// State management
let currentWorkshopId = "ws_demo";
let currentQuotationResult = null;
let currentItems = [];
let selectedFile = null;
let currentJobId = null;

// DOM Elements
const workshopIdInput = document.getElementById("workshopIdInput");
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const btnSelectFile = document.getElementById("btnSelectFile");
const btnStartQuotation = document.getElementById("btnStartQuotation");
const imagePreviewContainer = document.getElementById("imagePreviewContainer");
const imagePreview = document.getElementById("imagePreview");
const fileName = document.getElementById("fileName");
const btnRemoveFile = document.getElementById("btnRemoveFile");

const tableBody = document.getElementById("tableBody");
const grandTotalDisplay = document.getElementById("grandTotalDisplay");
const missingPriceBanner = document.getElementById("missingPriceBanner");
const pollingStatus = document.getElementById("pollingStatus");
const pollingText = document.getElementById("pollingText");

const btnAddItem = document.getElementById("btnAddItem");
const btnToggleOwnerCost = document.getElementById("btnToggleOwnerCost");
const ownerCostPanel = document.getElementById("ownerCostPanel");

const btnExportPDF = document.getElementById("btnExportPDF");
const btnExportZalo = document.getElementById("btnExportZalo");
const zaloModal = document.getElementById("zaloModal");
const zaloTextarea = document.getElementById("zaloTextarea");
const btnCloseZaloModal = document.getElementById("btnCloseZaloModal");
const btnCopyZalo = document.getElementById("btnCopyZalo");

// Init
document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
});

function setupEventListeners() {
    workshopIdInput.addEventListener("change", (e) => {
        currentWorkshopId = e.target.value.trim() || "ws_demo";
    });

    // Drag & Drop
    btnSelectFile.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", handleFileSelect);

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            setFile(e.dataTransfer.files[0]);
        }
    });

    btnRemoveFile.addEventListener("click", resetFile);
    btnStartQuotation.addEventListener("click", startQuotationUpload);

    // Preset buttons
    document.querySelectorAll(".btn-preset").forEach(btn => {
        btn.addEventListener("click", () => {
            const key = btn.getAttribute("data-preset");
            applyPresetTemplate(key);
        });
    });

    // Add Item
    btnAddItem.addEventListener("click", addNewRow);

    // Toggle Owner Panel
    btnToggleOwnerCost.addEventListener("click", () => {
        ownerCostPanel.classList.toggle("hidden");
    });

    // Export buttons
    btnExportPDF.addEventListener("click", exportPDF);
    btnExportZalo.addEventListener("click", exportZalo);
    btnCloseZaloModal.addEventListener("click", () => zaloModal.classList.add("hidden"));
    btnCopyZalo.addEventListener("click", copyZaloText);
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        setFile(e.target.files[0]);
    }
}

function setFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreviewContainer.classList.remove("hidden");
        dropZone.classList.add("hidden");
        btnStartQuotation.disabled = false;
    };
    reader.readAsDataURL(file);
}

function resetFile() {
    selectedFile = null;
    fileInput.value = "";
    imagePreview.src = "";
    imagePreviewContainer.classList.add("hidden");
    dropZone.classList.remove("hidden");
    btnStartQuotation.disabled = true;
}

async function startQuotationUpload() {
    if (!selectedFile) return;

    currentWorkshopId = workshopIdInput.value.trim() || "ws_demo";

    const formData = new FormData();
    formData.append("workshop_id", currentWorkshopId);
    formData.append("file", selectedFile);

    try {
        pollingStatus.classList.remove("hidden");
        pollingText.textContent = "Đang gửi bản vẽ và khởi tạo tác vụ bóc tách ngầm...";

        const res = await fetch("/api/v1/quotations/upload", {
            method: "POST",
            body: formData,
        });

        if (!res.ok) throw new Error("Upload bản vẽ thất bại");

        const data = await res.json();
        currentJobId = data.job_id;
        pollingText.textContent = "AI đang phân tích kích thước & đếm số lượng mộc...";

        // Start Polling
        pollJobStatus(currentJobId);

    } catch (err) {
        alert("Lỗi: " + err.message);
        pollingStatus.classList.add("hidden");
    }
}

async function pollJobStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/api/v1/quotations/jobs/${jobId}`);
            if (!res.ok) return;

            const data = await res.json();
            if (data.status === "COMPLETED") {
                clearInterval(interval);
                pollingStatus.classList.add("hidden");
                currentQuotationResult = data.result;
                renderQuotationResult(currentQuotationResult);
            } else if (data.status === "FAILED") {
                clearInterval(interval);
                pollingStatus.classList.add("hidden");
                alert("Xử lý AI thất bại: " + (data.error_message || "Unknown error"));
            }
        } catch (err) {
            console.error("Polling error:", err);
        }
    }, 1000);
}

async function applyPresetTemplate(templateKey) {
    currentWorkshopId = workshopIdInput.value.trim() || "ws_demo";
    try {
        const res = await fetch(`/api/v1/workshops/${currentWorkshopId}/pricing/preset?template_key=${templateKey}`, {
            method: "POST"
        });
        if (!res.ok) throw new Error("Áp dụng preset thất bại");

        alert(`Đã nạp thành công mẫu bảng giá preset '${templateKey}' cho xưởng!`);
        
        // Recalculate if we have items
        if (currentItems.length > 0) {
            triggerRecalculate();
        }
    } catch (err) {
        alert("Lỗi: " + err.message);
    }
}

function renderQuotationResult(result) {
    currentQuotationResult = result;
    currentItems = result.items.map(item => ({
        name: item.quoted_item.name,
        length: item.quoted_item.length,
        width: item.quoted_item.width,
        depth: item.quoted_item.depth,
        wood_type: item.quoted_item.wood_type,
        quantity: item.quoted_item.quantity,
        category: item.quoted_item.category,
        unit_price: item.unit_price
    }));

    renderTable();
    updateDisplays(result);
}

function renderTable() {
    tableBody.innerHTML = "";

    if (!currentQuotationResult || !currentQuotationResult.items || currentQuotationResult.items.length === 0) {
        tableBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="11">Chưa có dữ liệu. Vui lòng upload bản vẽ 3D để AI bóc tách hoặc thêm hạng mục mới.</td>
            </tr>
        `;
        return;
    }

    let hasUnfilledPrices = false;

    currentQuotationResult.items.forEach((item, index) => {
        const tr = document.createElement("tr");

        const isPriceWarning = item.unit_price === 0 || item.is_warning;
        if (item.unit_price === 0) hasUnfilledPrices = true;

        const warningBadge = item.is_warning ? `<span class="badge badge-danger" title="${item.warning_message || ''}">⚠️ Chưa có giá</span>` : '';

        tr.innerHTML = `
            <td style="text-align: center;">${index + 1}</td>
            <td>
                <input type="text" class="table-input" value="${item.quoted_item.name}" data-field="name" data-index="${index}">
                ${warningBadge}
            </td>
            <td><input type="number" class="table-input" value="${item.quoted_item.length}" data-field="length" data-index="${index}"></td>
            <td><input type="number" class="table-input" value="${item.quoted_item.width}" data-field="width" data-index="${index}"></td>
            <td style="text-align: center;"><strong>${item.unit}</strong></td>
            <td><input type="text" class="table-input" value="${item.quoted_item.wood_type || ''}" data-field="wood_type" data-index="${index}"></td>
            <td><input type="number" class="table-input" value="${item.quoted_item.quantity}" data-field="quantity" data-index="${index}"></td>
            <td><input type="text" class="table-input" value="${item.quoted_item.category}" data-field="category" data-index="${index}"></td>
            <td>
                <input type="number" class="table-input ${isPriceWarning ? 'input-warning' : ''}" value="${item.unit_price}" data-field="unit_price" data-index="${index}">
            </td>
            <td style="text-align: right; font-weight: bold; font-size: 14px;">
                ${item.total_price.toLocaleString('vi-VN')} đ
            </td>
            <td style="text-align: center;">
                <button class="btn-icon btn-delete" data-index="${index}">❌</button>
            </td>
        `;

        tableBody.appendChild(tr);
    });

    if (hasUnfilledPrices) {
        missingPriceBanner.classList.remove("hidden");
    } else {
        missingPriceBanner.classList.add("hidden");
    }

    // Input change listeners
    document.querySelectorAll(".table-input").forEach(input => {
        input.addEventListener("change", handleTableInputChange);
    });

    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt(e.target.getAttribute("data-index"));
            currentItems.splice(idx, 1);
            triggerRecalculate();
        });
    });
}

function handleTableInputChange(e) {
    const idx = parseInt(e.target.getAttribute("data-index"));
    const field = e.target.getAttribute("data-field");
    let val = e.target.value;

    if (["length", "width", "quantity", "unit_price"].includes(field)) {
        val = parseFloat(val) || 0;
    }

    currentItems[idx][field] = val;
    triggerRecalculate();
}

function addNewRow() {
    currentItems.push({
        name: "Hạng mục mộc mới",
        length: 2000,
        width: 600,
        depth: 600,
        wood_type: "mdf_melamine",
        quantity: 1,
        category: "Khác",
        unit_price: 0
    });
    triggerRecalculate();
}

async function triggerRecalculate() {
    currentWorkshopId = workshopIdInput.value.trim() || "ws_demo";

    try {
        const payload = {
            workshop_id: currentWorkshopId,
            items: currentItems.map(item => ({
                name: item.name,
                length: parseFloat(item.length) || 0,
                width: parseFloat(item.width) || 0,
                depth: parseFloat(item.depth) || 0,
                wood_type: item.wood_type,
                quantity: parseInt(item.quantity) || 1,
                category: item.category
            }))
        };

        const res = await fetch("/api/v1/quotations/recalculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Recalculate failed");

        const newResult = await res.json();
        currentQuotationResult = newResult;
        renderTable();
        updateDisplays(newResult);

    } catch (err) {
        console.error("Recalculate error:", err);
    }
}

function updateDisplays(result) {
    grandTotalDisplay.textContent = `${result.total_amount.toLocaleString('vi-VN')} VNĐ`;

    btnExportPDF.disabled = result.items.length === 0;
    btnExportZalo.disabled = result.items.length === 0;

    // Owner Cost breakdown
    let totalSheets = 0;
    let boardMaterialCost = 0;
    let laborCost = 0;
    let hardwareCost = 0;

    result.items.forEach(item => {
        if (item.cost_breakdown) {
            totalSheets += item.cost_breakdown.board_sheets_estimated;
            boardMaterialCost += item.cost_breakdown.board_material_cost;
            laborCost += item.cost_breakdown.labor_cost;
            hardwareCost += item.cost_breakdown.hardware_cost;
        }
    });

    document.getElementById("totalSheetsCount").textContent = `${totalSheets.toFixed(2)} tấm (kèm 15% hao hụt)`;
    document.getElementById("totalBoardMaterialCost").textContent = `${boardMaterialCost.toLocaleString('vi-VN')} VNĐ`;
    document.getElementById("totalLaborCost").textContent = `${laborCost.toLocaleString('vi-VN')} VNĐ`;
    document.getElementById("totalHardwareCost").textContent = `${hardwareCost.toLocaleString('vi-VN')} VNĐ`;
    document.getElementById("totalBaseCostDisplay").textContent = `${result.total_base_cost.toLocaleString('vi-VN')} VNĐ`;
    document.getElementById("grossProfitDisplay").textContent = `${result.gross_profit_amount.toLocaleString('vi-VN')} VNĐ`;
}

async function exportPDF() {
    if (!currentQuotationResult) return;
    try {
        const res = await fetch("/api/v1/quotations/export/html", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ quotation: currentQuotationResult, workshop_name: "Xưởng Mộc Nội Thất" })
        });
        const data = await res.json();

        const printWindow = window.open("", "_blank");
        printWindow.document.write(data.html);
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => printWindow.print(), 500);

    } catch (err) {
        alert("Lỗi xuất PDF: " + err.message);
    }
}

async function exportZalo() {
    if (!currentQuotationResult) return;
    try {
        const res = await fetch("/api/v1/quotations/export/zalo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ quotation: currentQuotationResult, workshop_name: "Xưởng Mộc Nội Thất" })
        });
        const data = await res.json();
        zaloTextarea.value = data.zalo_text;
        zaloModal.classList.remove("hidden");

    } catch (err) {
        alert("Lỗi xuất Zalo: " + err.message);
    }
}

function copyZaloText() {
    zaloTextarea.select();
    navigator.clipboard.writeText(zaloTextarea.value);
    alert("Đã sao chép nội dung báo giá gửi Zalo vào bộ nhớ tạm!");
}
