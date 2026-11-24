/* =========================================================
   DYNAMIC RISK INTELLIGENCE, SAFETY & THREAT IDENTIFICATION
   Main JavaScript
   ========================================================= */

"use strict";


/* =========================================================
   1. DOM READY
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeMobileNavigation();

    initializeUserMenu();

    initializeFlashMessages();

    initializeScrollReveal();

    initializeCurrentLocationButtons();

    initializeLocationForms();

    initializeSearchInteractions();

    initializeSafetyFilters();

    initializeSOS();

});


/* =========================================================
   2. MOBILE NAVIGATION
   ========================================================= */

function initializeMobileNavigation() {

    const menuButton =
        document.getElementById("mobileMenuButton");

    const navigation =
        document.getElementById("mainNavigation");


    if (!menuButton || !navigation) {
        return;
    }


    menuButton.addEventListener("click", () => {

        const isOpen =
            navigation.classList.toggle("mobile-open");

        menuButton.classList.toggle(
            "active",
            isOpen
        );

        menuButton.setAttribute(
            "aria-expanded",
            String(isOpen)
        );

    });


    /*
       Close the mobile menu after
       clicking a navigation link.
    */

    navigation
        .querySelectorAll("a")
        .forEach(link => {

            link.addEventListener("click", () => {

                navigation.classList.remove(
                    "mobile-open"
                );

                menuButton.classList.remove(
                    "active"
                );

                menuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

            });

        });


    /*
       Close menu when clicking outside.
    */

    document.addEventListener("click", event => {

        const clickedInsideNavigation =
            navigation.contains(event.target);

        const clickedMenuButton =
            menuButton.contains(event.target);


        if (
            !clickedInsideNavigation &&
            !clickedMenuButton
        ) {

            navigation.classList.remove(
                "mobile-open"
            );

            menuButton.classList.remove(
                "active"
            );

            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );

        }

    });

}


/* =========================================================
   3. USER DROPDOWN
   ========================================================= */

function initializeUserMenu() {

    const menu =
        document.querySelector(".user-menu");

    const button =
        document.getElementById("userMenuButton");

    const dropdown =
        document.getElementById("userDropdown");


    if (!menu || !button || !dropdown) {
        return;
    }


    button.addEventListener("click", event => {

        event.stopPropagation();

        menu.classList.toggle("open");

    });


    document.addEventListener("click", event => {

        if (!menu.contains(event.target)) {

            menu.classList.remove("open");

        }

    });

}


/* =========================================================
   4. FLASH MESSAGES
   ========================================================= */

function initializeFlashMessages() {

    const messages =
        document.querySelectorAll(".flash-message");


    if (!messages.length) {
        return;
    }


    messages.forEach(message => {

        /*
           Automatically remove ordinary
           flash messages after 6 seconds.
        */

        setTimeout(() => {

            if (
                message &&
                message.isConnected
            ) {

                message.style.opacity = "0";

                message.style.transform =
                    "translateX(15px)";

                setTimeout(() => {

                    if (
                        message &&
                        message.isConnected
                    ) {
                        message.remove();
                    }

                }, 250);

            }

        }, 6000);

    });

}


/* =========================================================
   5. SCROLL REVEAL
   ========================================================= */

function initializeScrollReveal() {

    const revealElements =
        document.querySelectorAll(".reveal");


    if (!revealElements.length) {
        return;
    }


    /*
       Browser does not support IntersectionObserver:
       show everything immediately.
    */

    if (
        !("IntersectionObserver" in window)
    ) {

        revealElements.forEach(element => {

            element.classList.add(
                "visible"
            );

        });

        return;

    }


    const observer =
        new IntersectionObserver(
            entries => {

                entries.forEach(entry => {

                    if (
                        entry.isIntersecting
                    ) {

                        entry.target.classList.add(
                            "visible"
                        );

                        observer.unobserve(
                            entry.target
                        );

                    }

                });

            },
            {
                threshold: 0.12,
                rootMargin: "0px 0px -30px 0px"
            }
        );


    revealElements.forEach(element => {

        observer.observe(element);

    });

}


/* =========================================================
   6. CURRENT LOCATION
   ========================================================= */

function initializeCurrentLocationButtons() {

    const buttons =
        document.querySelectorAll(
            "[data-current-location]"
        );


    if (!buttons.length) {
        return;
    }


    buttons.forEach(button => {

        button.addEventListener(
            "click",
            event => {

                event.preventDefault();

                detectCurrentLocation(
                    button
                );

            }
        );

    });

}


/* =========================================================
   7. GEOLOCATION FUNCTION
   ========================================================= */

function detectCurrentLocation(
    triggerButton = null
) {

    if (
        !navigator.geolocation
    ) {

        showLocationStatus(
            "Geolocation is not supported by this browser.",
            "error"
        );

        return;

    }


    /*
       Prevent double clicks.
    */

    if (
        triggerButton &&
        triggerButton.dataset.loading === "true"
    ) {

        return;

    }


    if (triggerButton) {

        triggerButton.dataset.loading =
            "true";

        triggerButton.classList.add(
            "loading"
        );

        triggerButton.disabled =
            true;

    }


    showLocationStatus(
        "Detecting your current location...",
        "loading"
    );


    navigator.geolocation.getCurrentPosition(

        position => {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            /*
               Put coordinates into any matching fields.
            */

            setLocationCoordinates(
                latitude,
                longitude
            );


            /*
               Update visible location text.
            */

            updateCurrentLocationText(
                latitude,
                longitude
            );


            showLocationStatus(
                "Location detected successfully.",
                "success"
            );


            finishLocationButton(
                triggerButton
            );

        },


        error => {

            let message =
                "Unable to detect your location.";


            switch (error.code) {

                case error.PERMISSION_DENIED:

                    message =
                        "Location permission was denied. Please allow location access in your browser.";

                    break;


                case error.POSITION_UNAVAILABLE:

                    message =
                        "Your current location is unavailable.";

                    break;


                case error.TIMEOUT:

                    message =
                        "Location detection timed out. Please try again.";

                    break;

            }


            showLocationStatus(
                message,
                "error"
            );


            finishLocationButton(
                triggerButton
            );

        },


        {
            enableHighAccuracy: true,

            timeout: 12000,

            maximumAge: 30000

        }

    );

}


/* =========================================================
   8. SET LOCATION COORDINATES
   ========================================================= */

function setLocationCoordinates(
    latitude,
    longitude
) {

    /*
       Navigation fields.
    */

    const startLat =
        document.getElementById(
            "startLat"
        );

    const startLon =
        document.getElementById(
            "startLon"
        );


    if (startLat) {

        startLat.value =
            latitude;

    }


    if (startLon) {

        startLon.value =
            longitude;

    }


    /*
       Generic fields used by
       Safety Map and other pages.
    */

    const latitudeInput =
        document.getElementById(
            "latitude"
        );

    const longitudeInput =
        document.getElementById(
            "longitude"
        );


    if (latitudeInput) {

        latitudeInput.value =
            latitude;

    }


    if (longitudeInput) {

        longitudeInput.value =
            longitude;

    }


    /*
       Generic data attributes.
    */

    document
        .querySelectorAll(
            "[data-latitude]"
        )
        .forEach(element => {

            if (
                "value" in element
            ) {

                element.value =
                    latitude;

            }

        });


    document
        .querySelectorAll(
            "[data-longitude]"
        )
        .forEach(element => {

            if (
                "value" in element
            ) {

                element.value =
                    longitude;

            }

        });


    /*
       Navigation start field.
       We use a hidden coordinate value so
       Flask can understand Current Location.
    */

    const startInput =
        document.getElementById(
            "startLocation"
        );


    if (startInput) {

        startInput.value =
            `${latitude},${longitude}`;

    }


    /*
       Safety Map hidden fields.
    */

    const mapLat =
        document.getElementById(
            "mapLatitude"
        );

    const mapLon =
        document.getElementById(
            "mapLongitude"
        );


    if (mapLat) {

        mapLat.value =
            latitude;

    }


    if (mapLon) {

        mapLon.value =
            longitude;

    }

}


/* =========================================================
   9. UPDATE LOCATION TEXT
   ========================================================= */

function updateCurrentLocationText(
    latitude,
    longitude
) {

    fetch(`/api/reverse-geocode?lat=${latitude}&lon=${longitude}`)
        .then(res => res.json())
        .then(data => {
            const locName = (data && data.success && data.locality) ? data.locality : "Mumbai Locality";
            document
                .querySelectorAll(
                    "[data-location-display]"
                )
                .forEach(element => {
                    element.textContent = locName;
                });

            document
                .querySelectorAll(
                    ".current-location-text"
                )
                .forEach(element => {
                    element.textContent = locName;
                });
        })
        .catch(() => {
            document
                .querySelectorAll(
                    "[data-location-display], .current-location-text"
                )
                .forEach(element => {
                    element.textContent = "Mumbai Locality";
                });
        });

}


/* =========================================================
   10. LOCATION STATUS
   ========================================================= */

function showLocationStatus(
    message,
    type = "loading"
) {

    const statusElements =
        document.querySelectorAll(
            ".location-status"
        );


    statusElements.forEach(element => {

        element.textContent =
            message;


        element.classList.remove(
            "success",
            "error"
        );


        if (
            type === "success"
        ) {

            element.classList.add(
                "success"
            );

        }


        if (
            type === "error"
        ) {

            element.classList.add(
                "error"
            );

        }


        const icon =
            element.querySelector("i");


        if (icon) {

            if (
                type === "loading"
            ) {

                icon.className =
                    "fa-solid fa-location-crosshairs fa-spin";

            } else if (
                type === "success"
            ) {

                icon.className =
                    "fa-solid fa-circle-check";

            } else {

                icon.className =
                    "fa-solid fa-circle-exclamation";

            }

        }

    });

}


/* =========================================================
   11. FINISH LOCATION BUTTON
   ========================================================= */

function finishLocationButton(
    button
) {

    if (!button) {
        return;
    }


    button.dataset.loading =
        "false";

    button.classList.remove(
        "loading"
    );

    button.disabled =
        false;

}


/* =========================================================
   12. LOCATION FORMS
   ========================================================= */

function initializeLocationForms() {

    const forms =
        document.querySelectorAll(
            "[data-location-form]"
        );


    forms.forEach(form => {

        form.addEventListener(
            "submit",
            event => {

                const startInput =
                    form.querySelector(
                        "[name='start']"
                    );

                const destinationInput =
                    form.querySelector(
                        "[name='destination']"
                    );


                /*
                   Navigation form with an empty
                   destination should not submit.
                */

                if (
                    destinationInput &&
                    !destinationInput.value.trim()
                ) {

                    event.preventDefault();

                    showFormError(
                        form,
                        "Please enter a destination."
                    );

                    destinationInput.focus();

                    return;

                }


                /*
                   Safe Route requires both fields.
                */

                if (
                    form.dataset.locationForm
                    === "route"
                ) {

                    if (
                        !startInput ||
                        !startInput.value.trim()
                    ) {

                        event.preventDefault();

                        showFormError(
                            form,
                            "Please enter a starting location."
                        );

                        if (startInput) {
                            startInput.focus();
                        }

                        return;

                    }

                }

            }
        );

    });

}


/* =========================================================
   13. FORM ERROR
   ========================================================= */

function showFormError(
    form,
    message
) {

    let error =
        form.querySelector(
            ".form-client-error"
        );


    if (!error) {

        error =
            document.createElement(
                "div"
            );

        error.className =
            "form-client-error error-box";


        form.prepend(
            error
        );

    }


    error.textContent =
        message;


    error.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });

}


/* =========================================================
   14. SEARCH INTERACTIONS
   ========================================================= */

function initializeSearchInteractions() {

    /*
       Popular search chips.
    */

    document
        .querySelectorAll(
            "[data-search-place]"
        )
        .forEach(chip => {

            chip.addEventListener(
                "click",
                () => {

                    const value =
                        chip.dataset.searchPlace;


                    const input =
                        document.querySelector(
                            "[name='location'], #placeSearch, #locationSearch"
                        );


                    if (input) {

                        input.value =
                            value;

                        input.focus();

                    }

                }
            );

        });


    /*
       Pressing Enter in custom search fields.
    */

    document
        .querySelectorAll(
            "[data-search-input]"
        )
        .forEach(input => {

            input.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter"
                    ) {

                        const form =
                            input.closest(
                                "form"
                            );


                        if (form) {

                            form.submit();

                        }

                    }

                }
            );

        });

}


/* =========================================================
   15. SAFETY MAP FILTERS
   ========================================================= */

function initializeSafetyFilters() {

    const filterButtons =
        document.querySelectorAll(
            "[data-service-filter]"
        );


    if (!filterButtons.length) {
        return;
    }


    filterButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const service =
                    button.dataset.serviceFilter;


                /*
                   Remove active state.
                */

                filterButtons.forEach(
                    item => {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                button.classList.add(
                    "active"
                );


                /*
                   If the page uses a form,
                   submit the selected service.
                */

                const form =
                    button.closest(
                        "form"
                    );


                if (form) {

                    const input =
                        form.querySelector(
                            "[name='service']"
                        );


                    if (input) {

                        input.value =
                            service;

                    }

                }


                /*
                   If a service category
                   is loaded dynamically,
                   allow page JS to handle it.
                */

                const event =
                    new CustomEvent(
                        "dristi:service-change",
                        {
                            detail: {
                                service: service
                            }
                        }
                    );


                document.dispatchEvent(
                    event
                );

            }
        );

    });

}


/* =========================================================
   16. SOS
   ========================================================= */

function initializeSOS() {

    const sosButton =
        document.getElementById(
            "sosButton"
        );


    if (!sosButton) {
        return;
    }


    sosButton.addEventListener(
        "click",
        event => {

            event.preventDefault();


            /*
               Confirmation prevents accidental
               SOS activation.
            */

            const confirmed =
                window.confirm(
                    "Are you sure you want to activate SOS?"
                );


            if (!confirmed) {
                return;
            }


            activateSOS(
                sosButton
            );

        }
    );

}


/* =========================================================
   17. ACTIVATE SOS
   ========================================================= */

function activateSOS(
    button
) {

    button.disabled =
        true;


    button.classList.add(
        "loading"
    );


    const originalHTML =
        button.innerHTML;


    button.innerHTML =
        `
        <i class="fa-solid fa-location-crosshairs fa-spin"></i>
        <span>DETECTING</span>
        `;


    /*
       SOS requires current location.
    */

    if (
        !navigator.geolocation
    ) {

        handleSOSError(
            button,
            originalHTML,
            "Location services are not supported by this browser."
        );

        return;

    }


    navigator.geolocation.getCurrentPosition(

        position => {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            /*
               Save location only in the
               current page state.
            */

            window.dristiSOSLocation = {

                latitude:
                    latitude,

                longitude:
                    longitude,

                timestamp:
                    new Date().toISOString()

            };
            window.safeGuardSOSLocation = window.dristiSOSLocation;


            updateSOSUI(
                latitude,
                longitude
            );


            button.disabled =
                false;


            button.classList.remove(
                "loading"
            );


            button.innerHTML =
                originalHTML;


            document.dispatchEvent(

                new CustomEvent(
                    "dristi:sos-activated",
                    {
                        detail: {
                            latitude:
                                latitude,

                            longitude:
                                longitude
                        }
                    }
                )

            );

        },


        error => {

            let message =
                "Could not determine your location.";


            if (
                error.code ===
                error.PERMISSION_DENIED
            ) {

                message =
                    "Location permission was denied. Please allow location access to use SOS location sharing.";

            }


            handleSOSError(
                button,
                originalHTML,
                message
            );

        },


        {
            enableHighAccuracy: true,

            timeout: 12000,

            maximumAge: 0

        }

    );

}


/* =========================================================
   18. UPDATE SOS UI
   ========================================================= */

function updateSOSUI(
    latitude,
    longitude
) {

    fetch(`/api/reverse-geocode?lat=${latitude}&lon=${longitude}`)
        .then(res => res.json())
        .then(data => {
            const locName = (data && data.success && data.locality) ? data.locality : "Mumbai Locality";
            document
                .querySelectorAll(
                    "[data-sos-location]"
                )
                .forEach(element => {
                    element.textContent = locName;
                });
        })
        .catch(() => {
            document
                .querySelectorAll(
                    "[data-sos-location]"
                )
                .forEach(element => {
                    element.textContent = "Mumbai Locality";
                });
        });


    document
        .querySelectorAll(
            "[data-sos-status]"
        )
        .forEach(element => {

            element.textContent =
                "Your current location is ready to share.";

            element.classList.add(
                "success"
            );

        });


    /*
       Create a shareable location URL.
    */

    const mapURL =
        `https://maps.google.com/?q=${encodeURIComponent(
            latitude
        )},${encodeURIComponent(
            longitude
        )}`;


    document
        .querySelectorAll(
            "[data-share-location]"
        )
        .forEach(button => {

            button.dataset.locationUrl =
                mapURL;

            button.disabled =
                false;

        });

}


/* =========================================================
   19. SOS ERROR
   ========================================================= */

function handleSOSError(
    button,
    originalHTML,
    message
) {

    button.disabled =
        false;


    button.classList.remove(
        "loading"
    );


    button.innerHTML =
        originalHTML;


    showSOSMessage(
        message,
        "error"
    );

}


/* =========================================================
   20. SOS MESSAGE
   ========================================================= */

function showSOSMessage(
    message,
    type = "error"
) {

    let box =
        document.getElementById(
            "sosMessage"
        );


    if (!box) {

        box =
            document.createElement(
                "div"
            );

        box.id =
            "sosMessage";

        box.className =
            "error-box";


        const container =
            document.querySelector(
                ".sos-container"
            )
            ||
            document.body;


        container.prepend(
            box
        );

    }


    box.textContent =
        message;


    box.classList.remove(
        "success",
        "error"
    );


    box.classList.add(
        type
    );

}


/* =========================================================
   21. SHARE LOCATION
   ========================================================= */

async function shareCurrentLocation() {

    const location =
        window.dristiSOSLocation || window.safeGuardSOSLocation;


    if (
        !location
    ) {

        showSOSMessage(
            "Activate SOS or detect your location first.",
            "error"
        );

        return;

    }


    const latitude =
        location.latitude;

    const longitude =
        location.longitude;


    const mapURL =
        `https://maps.google.com/?q=${encodeURIComponent(
            latitude
        )},${encodeURIComponent(
            longitude
        )}`;


    const message =
        [
            "Emergency! I need help.",
            "",
            `My current location: ${mapURL}`
        ].join("\n");


    /*
       Use the Web Share API when available.
    */

    if (
        navigator.share
    ) {

        try {

            await navigator.share({

                title:
                    "Dynamic Risk Intelligence Emergency Location",

                text:
                    message

            });


            showSOSMessage(
                "Location sharing opened successfully.",
                "success"
            );


            return;

        } catch (error) {

            /*
               User cancelled the native
               sharing window. Do nothing.
            */

            if (
                error.name ===
                "AbortError"
            ) {

                return;

            }

        }

    }


    /*
       Fallback: copy the emergency message.
    */

    try {

        await navigator.clipboard.writeText(
            message
        );


        showSOSMessage(
            "Emergency location message copied. You can paste it into a message or call.",
            "success"
        );


    } catch (error) {

        window.prompt(
            "Copy this emergency location:",
            message
        );

    }

}


/* =========================================================
   22. SHARE BUTTONS
   ========================================================= */

document.addEventListener(
    "click",
    event => {

        const button =
            event.target.closest(
                "[data-share-location]"
            );


        if (!button) {
            return;
        }


        event.preventDefault();


        shareCurrentLocation();

    }
);


/* =========================================================
   23. CALL BUTTONS
   ========================================================= */

document.addEventListener(
    "click",
    event => {

        const button =
            event.target.closest(
                "[data-call-number]"
            );


        if (!button) {
            return;
        }


        const number =
            button.dataset.callNumber;


        if (!number) {
            return;
        }


        /*
           Browser/mobile will hand the
           tel link to the device.
        */

        window.location.href =
            `tel:${number}`;

    }
);


/* =========================================================
   24. NAVIGATION HANDOFF
   ========================================================= */

/*
   Used by:

   Safe Route → Navigation
   Safety Map → Navigation
   SOS → Navigation

   Example:

   <a
       href="#"
       data-navigate-to="Marine Drive"
       data-navigate-start="Andheri"
   >
*/

document.addEventListener(
    "click",
    event => {

    })