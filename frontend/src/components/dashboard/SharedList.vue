<template>
  <div class="shared-list">
    <el-table :data="shares" v-loading="loading">
      <el-table-column label="文件名" prop="name">
         <template #default="scope">
           {{ scope.row.name }}
         </template>
      </el-table-column>
      <el-table-column label="接收者" prop="recipient_username" />
      <el-table-column label="分享时间" prop="created_at" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-popconfirm title="确定撤销此分享吗？对方将无法再访问。" @confirm="$emit('revoke', scope.row)">
            <template #reference>
              <el-button type="danger" size="small">撤销</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  shares: Array,
  loading: Boolean
})

defineEmits(['revoke'])
</script>
