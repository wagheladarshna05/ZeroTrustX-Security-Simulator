// ZeroTrustX dashboard interactions

(function () {

  "use strict";

  // Live clock
  function updateClock() {

    const now = new Date();
    const timeStr = now.toUTCString().split(" ")[4];

    const el = document.getElementById("liveTime");

    if (el) {
      el.textContent = timeStr + " UTC";
    }

  }

  updateClock();
  setInterval(updateClock, 1000);


  // Fullscreen
  const fullscreenIcon = document.querySelector(
    ".status-right .fa-expand"
  );

  if (fullscreenIcon) {

    fullscreenIcon.style.cursor = "pointer";

    fullscreenIcon.addEventListener("click", function () {

      if (!document.fullscreenElement) {

        document.documentElement.requestFullscreen()
          .catch(function (error) {
            console.log("Fullscreen error:", error);
          });

      } else {

        document.exitFullscreen();

      }

    });

  }


  // Notifications
  const bellIcon = document.querySelector(
    ".status-right .fa-bell"
  );

  if (bellIcon) {

    bellIcon.style.cursor = "pointer";

    bellIcon.addEventListener("click", function (event) {

      event.stopPropagation();

      let notificationPanel =
        document.getElementById("notificationPanel");

      if (notificationPanel) {

        notificationPanel.classList.toggle("show");
        return;

      }

      notificationPanel = document.createElement("div");

      notificationPanel.id = "notificationPanel";

      notificationPanel.style.position = "fixed";
      notificationPanel.style.top = "70px";
      notificationPanel.style.right = "25px";
      notificationPanel.style.width = "360px";
      notificationPanel.style.maxHeight = "420px";
      notificationPanel.style.overflowY = "auto";
      notificationPanel.style.background = "#101a26";
      notificationPanel.style.border = "1px solid #2a3f55";
      notificationPanel.style.borderRadius = "12px";
      notificationPanel.style.padding = "18px";
      notificationPanel.style.zIndex = "9999";
      notificationPanel.style.boxShadow =
        "0 10px 30px rgba(0,0,0,0.4)";

      notificationPanel.innerHTML = `
        <div style="
          display:flex;
          justify-content:space-between;
          align-items:center;
          margin-bottom:15px;
        ">

          <strong style="
            color:#ffffff;
            font-size:16px;
          ">
            <i class="fas fa-bell"></i>
            Security Notifications
          </strong>

          <span style="
            color:#7f8da3;
            font-size:12px;
          ">
            Recent alerts
          </span>

        </div>

        <div id="notificationContent"></div>

        <div style="
          margin-top:15px;
          padding-top:12px;
          border-top:1px solid #1d2633;
          text-align:center;
        ">

          <a href="/alerts"
             style="
               color:#00c8b6;
               text-decoration:none;
               font-size:13px;
             ">
            View all security alerts →
          </a>

        </div>
      `;

      document.body.appendChild(notificationPanel);

      const alertItems = document.querySelectorAll(
        ".alert-list .alert-item"
      );

      const content =
        document.getElementById("notificationContent");

      if (alertItems.length > 0) {

        let foundAlerts = false;

        alertItems.forEach(function (item) {

          const textElement =
            item.querySelector(".alert-text");

          const timeElement =
            item.querySelector(".alert-time");

          if (!textElement) {
            return;
          }

          const text =
            textElement.textContent.trim();

          if (text === "No active security alerts") {
            return;
          }

          foundAlerts = true;

          const time =
            timeElement
              ? timeElement.textContent.trim()
              : "";

          const notification =
            document.createElement("div");

          notification.style.padding = "12px";
          notification.style.marginBottom = "8px";
          notification.style.background = "#151f2d";
          notification.style.borderRadius = "8px";
          notification.style.fontSize = "12px";
          notification.style.color = "#c8d1dc";

          notification.innerHTML = `
            <div style="
              display:flex;
              gap:8px;
              align-items:flex-start;
            ">

              <i class="fas fa-circle-exclamation"
                 style="
                   color:#f47b7b;
                   margin-top:2px;
                 ">
              </i>

              <div style="flex:1;">

                <div style="
                  color:#ffffff;
                  line-height:1.4;
                ">
                  ${text}
                </div>

                <div style="
                  color:#7f8da3;
                  margin-top:5px;
                  font-size:11px;
                ">
                  ${time}
                </div>

              </div>

            </div>
          `;

          content.appendChild(notification);

        });

        if (!foundAlerts) {

          content.innerHTML = `
            <div style="
              text-align:center;
              padding:25px;
              color:#7f8da3;
            ">

              <i class="fas fa-shield-check"
                 style="
                   font-size:28px;
                   color:#3dd68c;
                   margin-bottom:10px;
                 ">
              </i>

              <div>
                No active security alerts
              </div>

            </div>
          `;

        }

      }

    });

  }


  // Profile
  const profileIcon = document.querySelector(
    ".sidebar-bottom .avatar"
  );

  if (profileIcon) {

    profileIcon.style.cursor = "pointer";

    profileIcon.addEventListener("click", function (event) {

      event.stopPropagation();

      let profilePanel =
        document.getElementById("profilePanel");

      if (profilePanel) {

        profilePanel.remove();
        return;

      }

      profilePanel = document.createElement("div");

      profilePanel.id = "profilePanel";

      profilePanel.style.position = "fixed";
      profilePanel.style.left = "75px";
      profilePanel.style.bottom = "25px";
      profilePanel.style.width = "260px";
      profilePanel.style.background = "#101a26";
      profilePanel.style.border = "1px solid #2a3f55";
      profilePanel.style.borderRadius = "12px";
      profilePanel.style.padding = "18px";
      profilePanel.style.zIndex = "9999";
      profilePanel.style.boxShadow =
        "0 10px 30px rgba(0,0,0,0.4)";

      profilePanel.innerHTML = `

        <div style="
          display:flex;
          align-items:center;
          gap:12px;
          margin-bottom:15px;
        ">

          <div style="
            width:42px;
            height:42px;
            border-radius:50%;
            background:#182536;
            display:flex;
            align-items:center;
            justify-content:center;
          ">

            <i class="fas fa-user-astronaut"
               style="
                 color:#00c8b6;
                 font-size:20px;
               ">
            </i>

          </div>

          <div>

            <div style="
              color:#ffffff;
              font-weight:600;
            ">
              ZeroTrustX User
            </div>

            <div style="
              color:#7f8da3;
              font-size:11px;
            ">
              Security Dashboard
            </div>

          </div>

        </div>

        <div style="
          border-top:1px solid #1d2633;
          padding-top:12px;
        ">

          <div style="
            color:#7f8da3;
            font-size:11px;
            margin-bottom:4px;
          ">
            SYSTEM STATUS
          </div>

          <div style="
            color:#3dd68c;
            font-size:13px;
            margin-bottom:12px;
          ">
            <i class="fas fa-circle"></i>
            Zero Trust Active
          </div>

          <div style="
            color:#7f8da3;
            font-size:11px;
            margin-bottom:4px;
          ">
            VERIFICATION
          </div>

          <div style="
            color:#ffffff;
            font-size:13px;
          ">
            <i class="fas fa-shield-halved"></i>
            Continuous Verification
          </div>

        </div>

      `;

      document.body.appendChild(profilePanel);

    });

  }


  // Close panels
  document.addEventListener("click", function () {

    const notificationPanel =
      document.getElementById("notificationPanel");

    if (notificationPanel) {
      notificationPanel.classList.remove("show");
    }

    const profilePanel =
      document.getElementById("profilePanel");

    if (profilePanel) {
      profilePanel.remove();
    }

  });


  console.log("ZeroTrustX dashboard ready");

})();