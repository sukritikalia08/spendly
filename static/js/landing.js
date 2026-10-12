// ------------------------------------------------------------------ //
// "See how it works" video modal                                      //
// ------------------------------------------------------------------ //

(function () {
    const modal = document.getElementById("video-modal");
    const openBtn = document.getElementById("video-modal-open");
    const closeBtn = document.getElementById("video-modal-close");
    const iframe = document.getElementById("video-modal-iframe");

    if (!modal || !openBtn || !closeBtn || !iframe) return;

    function openModal() {
        // Load the video only when opened, so it starts fresh each time
        iframe.src = iframe.dataset.src;
        modal.hidden = false;
        document.body.style.overflow = "hidden";
        closeBtn.focus();
    }

    function closeModal() {
        // Clearing the src unloads the player, which stops playback
        iframe.src = "";
        modal.hidden = true;
        document.body.style.overflow = "";
        openBtn.focus();
    }

    openBtn.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);

    // Close when clicking the dark overlay, but not the video itself
    modal.addEventListener("click", function (e) {
        if (e.target === modal) closeModal();
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !modal.hidden) closeModal();
    });
})();
