(function () {
  console.log("ready!"); // sanity check
})();

const deleteButtons = document.getElementsByClassName("delete-entry");

for (var i = 0; i < deleteButtons.length; i++) {
  deleteButtons[i].addEventListener("click", function () {
    const postId = this.getAttribute("data-id");
    const node = this.closest("li");
    fetch(`/delete/${postId}`)
      .then(function (resp) {
        return resp.json();
      })
      .then(function (result) {
        if (result.status === 1) {
          node.parentNode.removeChild(node);
          console.log(result);
        }
        location.reload();
      })
      .catch(function (err) {
        console.log(err);
      });
  });
}
