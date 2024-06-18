let loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();

  let username = document.getElementById("username");
  let password = document.getElementById("pass");

  const apiUrl = `/login/${username.value}/${password.value}`;
    fetch(apiUrl)
        .then(response => response.json())
        .then((data)=>{
            if (data['status'] == "success")
            {
                window.location.href = `/board?username=${username.value}`;
            }
            else
            {
                var element = document.getElementById("error");
                element.classList.add("error-style");
                var element = document.getElementById("button");
                element.classList.add("button-error-style");
                var element = document.getElementById("signup");
                element.classList.add("signup-error-style");

            }
        })
});

