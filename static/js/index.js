const showOptions = (popoverID) => {
    const splittedID = popoverID.split('-');
    const indicatorID = splittedID[2];
    const popoverContentID = `popover-content-${indicatorID}`;

    const popover = document.querySelector(`#${popoverContentID}`);

    popover.classList.toggle('hidden');
}