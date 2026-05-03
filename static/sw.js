self.addEventListener("push", function(event) {
    const data = event.data.json();

    self.registration.showNotification("CCTV Alert", {
        body: data.message,
    });
});