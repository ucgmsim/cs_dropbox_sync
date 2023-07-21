import React from "react";
import "assets/InstallCard.css";
import step2 from "assets/images/step2.png";
import step3 from "assets/images/step3.png";
import step4 from "assets/images/step4.png";
import step5 from "assets/images/step5.png";

const InstallCard = () => {
  const userAgent = navigator.userAgent.toLowerCase();

  const getInstallationLink = () => {
    if (userAgent.includes("chrome")) {
      return "https://chrome.google.com/webstore/detail/downthemall/nljkibfhlpcnanjgbnlnbjecgicbjkge";
    } else if (userAgent.includes("edg")) {
      return "https://microsoftedge.microsoft.com/addons/detail/downthemall/kenmkleahlilpehjignjigpdhciknmdf";
    } else if (userAgent.includes("firefox")) {
      return "https://addons.mozilla.org/en-US/firefox/addon/downthemall/";
    } else {
      return null;
    }
  };

  const renderInstallationLink = () => {
    const installationLink = getInstallationLink();

    if (installationLink) {
      return (
        <a
          href={installationLink}
          target="_blank"
          rel="noopener noreferrer"
          className="installation-link"
        >
          Install DownThemAll Extension
        </a>
      );
    } else {
      return (
        <p className="browser-support-message">
          The DownThemAll extension only supports Chrome, Edge, and Firefox.
          Please use one of these browsers to download multiple files at once.
        </p>
      );
    }
  };

  return (
    <div className="installation-card">
      <h2 className="installation-card__title">
        Download using DownThemAll Extension
      </h2>
      <p className="installation-card__description">
        Downloading multiple files from websites can be challenging with some
        browsers. The DownThemAll extension provides a convenient solution by
        allowing you to download multiple files effortlessly. Follow the steps
        below to install the extension in your preferred browser and use it to
        download the files.
      </p>
      <div className="installation-steps">
        <div className="installation-step">
          <div className="installation-step__content">
            <h3>Step 1:</h3>
            <h3>Install Extension</h3>
            <p>{renderInstallationLink()}</p>
          </div>
        </div>
        <div className="installation-step">
          <div className="installation-step__content">
            <h3>Step 2:</h3>
            <h3>Activate Extension</h3>
            <p>
              Click the extension icon in your browser's toolbar and then select
              at the top DownThemAll!
            </p>
            <img src={step2} alt="Extension Screenshot" />
          </div>
        </div>
        <div className="installation-step">
          <div className="installation-step__content">
            <h3>Step 3:</h3>
            <h3>Select All Files</h3>
            <p>
              Select the "All Files" option from the extension menu and remove
              the top link which is the install extension link.
            </p>
            <img src={step3} alt="Select All File Screenshot" />
          </div>
        </div>
        <div className="installation-step">
          <div className="installation-step__content">
            <h3>Step 4:</h3>
            <h3>Download</h3>
            <p>
              Click the "Download" button to start the download. (You can select
              a subfolder in your downloads folder if you wish and have alot of
              files selected)
            </p>
            <img src={step4} alt="Download Screenshot" />
          </div>
        </div>
        <div>
          <div className="installation-step__content">
            <h3>Step 5:</h3>
            <h3>Download Manager</h3>
            <p>
              You will then be taken to the download manager which tracks each
              of your downloads in progress.
            </p>
            <img
              className="installation-manager-img"
              src={step5}
              alt="Download Manager Screenshot"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstallCard;
