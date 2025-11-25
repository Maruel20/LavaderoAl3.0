import * as bootstrap from "bootstrap"

export function useBootstrap() {
  const showModal = (modalId) => {
    const modalElement = document.getElementById(modalId)
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement)
      modal.show()
    }
  }

  const hideModal = (modalId) => {
    const modalElement = document.getElementById(modalId)
    if (modalElement) {
      const modal = bootstrap.Modal.getInstance(modalElement)
      if (modal) {
        modal.hide()
      }
    }
  }

  return {
    showModal,
    hideModal,
  }
}
