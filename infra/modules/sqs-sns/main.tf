variable "project" { type = string }
variable "env" { type = string }

resource "aws_sqs_queue" "tasks" {
  name                       = "${var.project}-${var.env}-tasks"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400
}

resource "aws_sqs_queue" "tasks_dlq" {
  name = "${var.project}-${var.env}-tasks-dlq"
}

resource "aws_sns_topic" "notifications" {
  name = "${var.project}-${var.env}-notifications"
}

output "task_queue_url" { value = aws_sqs_queue.tasks.url }
output "task_queue_arn" { value = aws_sqs_queue.tasks.arn }
output "notification_topic_arn" { value = aws_sns_topic.notifications.arn }
