'use client'
import type { FC } from 'react'
import * as React from 'react'
import {
  useCSVDownloader,
} from 'react-papaparse'

const CSV_TEMPLATE = [
  ['name', 'email', 'password', 'role', 'department'],
  ['张三', 'zhangsan@example.com', 'Password123', 'user', '研发部'],
  ['李四', 'lisi@example.com', '', 'dev', '产品部'],
  ['王五', 'wangwu@example.com', 'Pass456', 'manager', ''],
  ['赵六', 'zhaoliu@example.com', '', 'user', ''],
]

const DownloadTemplate: FC = () => {
  const { CSVDownloader, Type } = useCSVDownloader()

  return (
    <div className="mt-6">
      <div className="system-sm-medium text-text-primary">CSV 样板文件格式</div>
      <div className="mt-2 max-h-[300px] overflow-auto">
        <table className="w-full table-fixed border-separate border-spacing-0 rounded-lg border border-divider-regular text-xs">
          <thead className="text-text-tertiary">
            <tr>
              <td className="h-9 border-b border-divider-regular pr-2 pl-3">name</td>
              <td className="h-9 border-b border-divider-regular pr-2 pl-3">email</td>
              <td className="h-9 border-b border-divider-regular pr-2 pl-3">password</td>
              <td className="h-9 border-b border-divider-regular pr-2 pl-3">role</td>
              <td className="h-9 border-b border-divider-regular pr-2 pl-3">department</td>
            </tr>
          </thead>
          <tbody className="text-text-secondary">
            <tr>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">张三</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">zhangsan@example.com</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">Password123</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">user</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">研发部</td>
            </tr>
            <tr>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">李四</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">lisi@example.com</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">（不填则自动生成）</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">dev</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">产品部</td>
            </tr>
            <tr>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">王五</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">wangwu@example.com</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">Pass456</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">manager</td>
              <td className="h-9 border-b border-divider-subtle pr-2 pl-3 text-[13px]">（不填则不分配部门）</td>
            </tr>
            <tr>
              <td className="h-9 pr-2 pl-3 text-[13px]">赵六</td>
              <td className="h-9 pr-2 pl-3 text-[13px]">zhaoliu@example.com</td>
              <td className="h-9 pr-2 pl-3 text-[13px]">（不填则自动生成）</td>
              <td className="h-9 pr-2 pl-3 text-[13px]">user</td>
              <td className="h-9 pr-2 pl-3 text-[13px]">（不填则不分配部门）</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-text-tertiary">
        <CSVDownloader
          className="hover:text-text-accent-hover flex cursor-pointer items-center gap-1 text-text-accent"
          type={Type.Link}
          filename="user_import_template"
          bom={true}
          data={CSV_TEMPLATE}
        >
          <span className="i-custom-vender-solid-general-download-02 h-3 w-3" />
          下载 CSV 样板
        </CSVDownloader>
        <span>|</span>
        <span>密码不填则自动生成，角色不填默认为 user</span>
      </div>
    </div>
  )
}
export default React.memo(DownloadTemplate)
