import './ConfirmDialog.css'

interface Props {
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({ message, onConfirm, onCancel }: Props) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <p className="confirm-message">{message}</p>
        <div className="confirm-actions">
          <button className="confirm-btn confirm-cancel" onClick={onCancel}>取消</button>
          <button className="confirm-btn confirm-ok" onClick={onConfirm}>确认</button>
        </div>
      </div>
    </div>
  )
}
