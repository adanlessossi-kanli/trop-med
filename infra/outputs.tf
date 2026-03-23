output "alb_dns" {
  value = module.ecs.alb_dns
}

output "cloudfront_domain" {
  value = module.cloudfront.domain_name
}

output "s3_bucket" {
  value = module.s3.files_bucket
}

output "sqs_queue_url" {
  value = module.sqs_sns.task_queue_url
}

output "sns_topic_arn" {
  value = module.sqs_sns.notification_topic_arn
}

output "redis_endpoint" {
  value = module.elasticache.endpoint
}

output "gpu_instance_ip" {
  value = module.ec2_gpu.private_ip
}
